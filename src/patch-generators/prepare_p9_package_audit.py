"""Adapt the separate P8 crypto/parser audit to the exact P8-to-P9 delta."""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];source=R/'analysis/dev006/audit_p8.py'
t=source.read_text('utf8')
changes=[
 ('Separate-parser P8 package/SELF/ELF scope and crypto readback','Separate-parser P9 package/SELF/ELF scope and crypto readback'),
 ("O=ROOT/'analysis/p8-review'","O=ROOT/'analysis/p9-review'"),
 ("a=(ROOT/'candidates/HDD2TB-P5/PS3/UPDATE/PS3UPDAT.PUP').read_bytes();b=(ROOT/'candidates/HDD2TB-P8/PS3/UPDATE/PS3UPDAT.PUP').read_bytes()","a=(ROOT/'candidates/HDD2TB-P8/PS3/UPDATE/PS3UPDAT.PUP').read_bytes();b=(ROOT/'candidates/HDD2TB-P9/PS3/UPDATE/PS3UPDAT.PUP').read_bytes()"),
 ("assert sha(a)=='50cd0445ec64b801dbd6775fd8f448f61e91fd481ce50a73d54ddb2918281fd1'","assert sha(a)=='d0260ed27fb2a9fa50b140c7f439ef5653ec231c0fc983fce51e3b054aa1a47a'"),
 ("candidates/HDD2TB-P8/build-manifest.json","candidates/HDD2TB-P9/build-manifest.json"),
 ("analysis/candidate-p8-v2/PS3/UPDATE/PS3UPDAT.PUP","analysis/candidate-p9-v2/PS3/UPDATE/PS3UPDAT.PUP"),
 ("'P5 flash'","'P8 flash'"),("'P8 flash','PKG'","'P9 flash','PKG'"),
 ("'P8 header'","'P9 header'"),
 ("'P5 utility'","'P8 utility'"),("'P8 utility','SELF'","'P9 utility','SELF'"),
 ("oldelf=common.decode_both(old,'utility-P5');newelf=common.decode_both(new,'utility-P8')","oldelf=common.decode_both(old,'utility-P8');newelf=common.decode_both(new,'utility-P9')"),
 ("assert sha(oldelf)=='6fdcb1ab4a25c29230dbd5fdf0f2594ee8c9c5187ee3c13dbd384128c2504b9a'","assert sha(oldelf)=='b7e65e2dd7d82aa5c9957c2af7a192f475ed26f4140f3ab25ea18866bed53f01'"),
 ("analysis/dev006/p8-native/manifest.json","analysis/dev006/p9-safety-v2/manifest.json"),
 ("analysis/dev006/p8-native/libfs_utility_init-p8.elf","analysis/dev006/p9-safety-v2/libfs_utility_init-p9.elf"),
 ("assert nrr[:len(orr)]==orr and len(nrr)==len(orr)+16","assert nrr==orr and nh==oh"),
 ("for at in (0x10ea0,0x10ec8,0xea58,0xe6f8,0xe788,0xe9d8,0x186f0):y[0][at:at+4]=x[0][at:at+4]\n  assert x[0]==y[0][:len(x[0])] and x[1]==y[1]","for at in (0x16888,0x16894,0xe728):y[0][at:at+4]=x[0][at:at+4]\n  y[0][0x26400:0x264fc]=x[0][0x26400:0x264fc]\n  assert x==y"),
 ("analysis/dev006/p8-native/dataflow-audit.json","analysis/dev006/p9-safety-model-v3/result.json"),
 ("'P5_sysconf_unchanged':True","'P8_sysconf_unchanged':True"),
 ("'original_loaded_bytes_preserved_except_seven_hooks_four_base_pairs':True","'P8_loaded_bytes_preserved_except_three_hooks_and252_helper_bytes_four_base_pairs':True"),
 ("'original_relocations_preserved_sixteen_owned_address_relocations_added':True","'P8_relocations_and_program_headers_exactly_preserved':True")]
for a,b in changes:
    assert a in t,a;t=t.replace(a,b)
# Correct old/new descriptive labels independently of the assertions above.
t=t.replace("audit(au[PACKAGE],'P9 flash','PKG')","audit(au[PACKAGE],'P8 flash','PKG')")
t=t.replace("audit(old,'P9 utility','SELF')","audit(old,'P8 utility','SELF')")
with (R/'analysis/dev006/audit_p9.py').open('x',encoding='utf8') as f:f.write(t)
with (R/'analysis/dev006/p9-package-audit-provenance.json').open('x',encoding='utf8') as f:
    json.dump({'source':'analysis/dev006/audit_p8.py','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
      'destination':'analysis/dev006/audit_p9.py','changes':changes,'prior_audit_modified_or_executed':False},f,indent=2)
print('P9 separate package audit prepared; prior audit preserved.')
