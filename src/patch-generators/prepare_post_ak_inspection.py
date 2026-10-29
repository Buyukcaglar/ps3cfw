"""Prepare a new read-only diagnostic route; preserve the refused strict capture."""
import ast
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parents[2]
O = R / 'analysis/dev006/pny-post-ak-inspection-v1'


def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def put(path, text):
    with path.open('x', encoding='utf8') as f:
        f.write(text)


def main():
    stopped = json.loads((R / 'observations/HW002AL/private/pny-preservation-post-ak-v1/stopped.json').read_text('utf8'))
    assert stopped['message'] == 'Allocated inode is unreachable from root.' and not stopped['physicalWrites']
    parent = R / 'analysis/dev006/pny-post-ak-preservation-v1/Program.cs'
    source = parent.read_text('utf8').replace('pny-preservation-post-ak-v1', 'pny-post-ak-diagnostic-v1').replace(
        '--capture-strict', '--inspect-strict')
    source = source.replace('using PS3HddTool.Core.FileSystem;', 'using PS3HddTool.Core.FileSystem;\nusing System.Reflection;\nusing System.Collections;')
    source = source.replace('TargetPreservationReport report;long readBytes', 'object report;long readBytes')
    begin = source.index('        var request=new DirectRequest(')
    end = source.index('\n        // Read only three fixed HDD controls', begin)
    source = source[:begin] + '''
        using(var decodedStrict=new DecryptedDiskSourceCbc(new NonDisposingDiskSource(target),keys.AtaDataKey,true))
        using(var cache=new MetadataCache(decodedStrict,Path.Combine(session,"decoded-read-cache.bin")))
        {
            Type type=typeof(TargetPreservation).Assembly.GetType("PS3HddTool.Core.Migration.UfsVolume",true)!;
            const BindingFlags flags=BindingFlags.Instance|BindingFlags.Public|BindingFlags.NonPublic;
            object volume=type.GetConstructor(flags,null,new[]{typeof(IDiskSource),typeof(long),typeof(bool)},null)!.Invoke(new object[]{cache,32L,false});
            object Field(object value,string name)=>value.GetType().GetField(name,flags)!.GetValue(value)!;
            int I32(byte[] bytes,int at)=>BinaryPrimitives.ReadInt32BigEndian(bytes.AsSpan(at));
            long I64(byte[] bytes,int at)=>BinaryPrimitives.ReadInt64BigEndian(bytes.AsSpan(at));
            string? strictError=null;
            try{type.GetMethod("Inventory",flags)!.Invoke(volume,new object?[]{false,cancel.Token,
                (Action<MigrationProgress>)(p=>Emit(new{phase="strict-diagnostic",progress=p,physicalWrites=false})),"inspection"});}
            catch(TargetInvocationException e) when(e.InnerException is InvalidDataException)
            {strictError=e.InnerException!.Message;if(strictError!="Allocated inode is unreachable from root.")throw;}
            var nodes=(IDictionary)Field(volume,"Nodes");
            var nodeRows=new List<object>();
            foreach(DictionaryEntry pair in nodes)
            {
                var node=pair.Value!;byte[] raw=(byte[])Field(node,"Raw");
                nodeRows.Add(new{inode=(long)pair.Key,path=FieldNullable(node,"Path"),raw=Convert.ToHexString(raw),
                    type=BinaryPrimitives.ReadUInt16BigEndian(raw)>>12,size=I64(raw,0x10),sectors=I64(raw,0x18),
                    links=BinaryPrimitives.ReadInt16BigEndian(raw.AsSpan(2))});
            }
            SaveNew("reachable-nodes.json",nodeRows);
            byte[] super=(byte[])Field(volume,"Super");
            int ipg=(int)Field(volume,"Ipg"),fpg=(int)Field(volume,"Fpg"),fragment=(int)Field(volume,"Fragment"),
                iblk=(int)Field(volume,"Iblk"),dblk=(int)Field(volume,"Dblk");
            long offset=(long)Field(volume,"Offset"),size=(long)Field(volume,"Size");
            var groups=(Array)Field(volume,"Groups");
            var owned=(byte[][])Field(volume,"_owned");
            var orphanRows=new List<object>();long allocated=0,unowned=0,reservedFree=0;
            var samples=new List<long>();
            bool Bit(byte[] b,int start,int n)=>(b[start+n/8]&(1<<(n%8)))!=0;
            int sblk=I32(super,8);long cs=I64(super,0x448);int cssize=I32(super,0x9c);
            foreach(var item in groups)
            {
                cancel.Token.ThrowIfCancellationRequested();
                byte[] raw=(byte[])Field(item!,"Raw");int group=(int)Field(item!,"Number"),
                    imap=I32(raw,0x5c),fmap=I32(raw,0x60),fragments=I32(raw,0x14);
                for(int i=0;i<ipg;i++)if(Bit(raw,imap,i))
                {
                    allocated++;long ino=checked((long)group*ipg+i);
                    if(ino<=1||nodes.Contains(ino))continue;
                    if(orphanRows.Count>=4096)throw new InvalidDataException("Diagnostic orphan count budget");
                    long at=checked(offset+((long)group*fpg+iblk)*fragment+(long)i*256);
                    byte[] inode=cache.ReadBytes(at,256);
                    orphanRows.Add(new{inode=ino,group,index=i,offset=at,raw=Convert.ToHexString(inode),
                        type=BinaryPrimitives.ReadUInt16BigEndian(inode)>>12,size=I64(inode,0x10),
                        sectors=I64(inode,0x18),links=BinaryPrimitives.ReadInt16BigEndian(inode.AsSpan(2)),
                        all_zero=inode.AsSpan().ContainsAnyExcept((byte)0)==false});
                }
                for(int i=0;i<fragments;i++)
                {
                    long f=(long)group*fpg+i;
                    bool reserved=(i<dblk&&(group==0||i>=sblk))||(f>=cs&&f<cs+cssize/fragment),
                        free=Bit(raw,fmap,i);
                    if(reserved&&free)reservedFree++;
                    if(!reserved&&!free&&!Bit(owned[group],0,i))
                    {unowned++;if(samples.Count<4096)samples.Add(f);}
                }
            }
            SaveNew("unreachable-inodes.json",orphanRows);
            report=new{strictError,strict_preservation_qualified=strictError is null,
                reachable_nodes=nodes.Count,allocated_inode_bits_including_reserved=allocated,
                unreachable_inode_count=orphanRows.Count,unreachable_inodes=orphanRows,
                fragments_not_owned_by_reachable_tree=unowned,unowned_fragment_samples=samples,
                orphan_extent_ownership_not_yet_included=true,reserved_fragments_marked_free=reservedFree,
                native_size_fragments=size,group_count=groups.Length,block=(int)Field(volume,"Block"),fragment,
                ipg,fpg,iblk,dblk,clean=super[0xd1],pending_blocks=I64(super,0x450),
                pending_inodes=I32(super,0x458),physicalWrites=false,
                cache_records=cache.Records,cache_bytes=cache.Bytes};
            SaveNew("inspection.json",report);
            object? FieldNullable(object value,string name)=>value.GetType().GetField(name,flags)!.GetValue(value);
        }
''' + source[end:]
    source = source.replace('archive=report,archiveDirectory=Path.Combine(session,"target-archive"),',
                            'inspection=report,preservationArchiveCreated=false,')
    source = source.replace('phase="complete",archive=report,', 'phase="complete",inspection=report,')
    source += '''

sealed class MetadataCache(IDiskSource source,string path):IDiskSource
{
    private readonly FileStream _file=new(path,FileMode.CreateNew,FileAccess.Write,FileShare.Read);
    private readonly HashSet<(long,int)> _seen=new();
    public long Records{get;private set;}public long Bytes{get;private set;}
    public string Identity=>source.Identity;public long TotalSize=>source.TotalSize;public int SectorSize=>source.SectorSize;
    public long SectorCount=>source.SectorCount;public bool CanWrite=>false;public string Description=>source.Description;
    public byte[] ReadBytes(long at,int count)
    {
        byte[] data=source.ReadBytes(at,count);
        if(_seen.Add((at,count)))
        {
            byte[] header=new byte[44];BinaryPrimitives.WriteInt64LittleEndian(header,at);
            BinaryPrimitives.WriteInt32LittleEndian(header.AsSpan(8),count);
            using var sha=IncrementalHash.CreateHash(HashAlgorithmName.SHA256);sha.AppendData(header.AsSpan(0,12));sha.AppendData(data);
            sha.GetHashAndReset().CopyTo(header,12);_file.Write(header);_file.Write(data);Records++;Bytes+=data.Length;
        }
        return data;
    }
    public byte[] ReadSectors(long at,int count)=>ReadBytes(checked(at*512),checked(count*512));
    public void WriteBytes(long at,byte[] data)=>throw new InvalidOperationException("Read-only metadata cache");
    public void WriteBytes(long at,ReadOnlySpan<byte> data)=>throw new InvalidOperationException("Read-only metadata cache");
    public void WriteSectors(long at,byte[] data)=>throw new InvalidOperationException("Read-only metadata cache");
    public void Dispose(){_file.Flush(true);_file.Dispose();}
}
'''
    O.mkdir(exist_ok=False)
    put(O / 'Program.cs', source)
    project = R / 'analysis/dev006/pny-post-ak-preservation-v1/PostAkPnyPreservation.csproj'
    put(O / 'PostAkPnyDiagnostic.csproj', project.read_text('utf8'))
    parent_wrapper = R / 'tools/Capture-HW002AL-PostAkPny.ps1'
    wrapper = parent_wrapper.read_text('utf8').replace('current-capture-review.json', 'diagnostic-review.json').replace(
        'read_only_current_PNY_preservation_approved', 'read_only_current_PNY_diagnostic_approved').replace(
        'pny-preservation-post-ak-v1', 'pny-post-ak-diagnostic-v1').replace(
        'pny-post-ak-preservation-v1', 'pny-post-ak-inspection-v1').replace(
        'PostAkPnyPreservation.dll', 'PostAkPnyDiagnostic.dll').replace('--capture-strict', '--inspect-strict')
    put(R / 'tools/Inspect-HW002AL-PostAkPny.ps1', wrapper)
    put(O / 'source-provenance.json', json.dumps({
        'parent': str(parent.relative_to(R)), 'parent_sha256': sha(parent),
        'source_sha256': sha(O / 'Program.cs'),
        'wrapper_parent': str(parent_wrapper.relative_to(R)), 'wrapper_parent_sha256': sha(parent_wrapper),
        'changes': ['New diagnostic-only namespace and mode',
                    'Invoke only frozen UfsVolume constructor and Inventory(false) via reflection',
                    'Inspect existing fields after exact unreachable-inode rejection, enumerate bitmaps/raw inodes',
                    'Save hashed decoded metadata reads, reachable nodes and bounded orphan records',
                    'No strict-validation bypass, archive creation or physical write'],
        'shared_or_private_Core_modified_or_rebuilt': False, 'physical_IO': False}, indent=2) + '\n')
    print(json.dumps({'diagnostic_only_sources_prepared': True, 'physical_IO': False}))


if __name__ == '__main__':
    main()
