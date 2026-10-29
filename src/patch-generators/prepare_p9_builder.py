"""Create a P8-template P9 packager without editing prior candidate builders."""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[2]
src=R/'tools/build_hdd2tb_p8.py';text=src.read_text('utf8');changes=[
 ('P5 plus offline-built native allocation diagnostic; no device access.','P8 plus bounded checker allocation-failure guards; no device access.'),
 ("PARENT='50cd0445ec64b801dbd6775fd8f448f61e91fd481ce50a73d54ddb2918281fd1'","PARENT='d0260ed27fb2a9fa50b140c7f439ef5653ec231c0fc983fce51e3b054aa1a47a'"),
 ("candidates/HDD2TB-P5/PS3/UPDATE/PS3UPDAT.PUP","candidates/HDD2TB-P8/PS3/UPDATE/PS3UPDAT.PUP"),
 ("assert oldself==(ROOT/'analysis/flash'/MEMBER).read_bytes()","assert b.sha(oldself)=='5c1b2c1a9b894e6a091869fa30a5254f3191c45c2781485b82d5c73414a82153'"),
 ("assert b.sha(old)=='6fdcb1ab4a25c29230dbd5fdf0f2594ee8c9c5187ee3c13dbd384128c2504b9a'","assert b.sha(old)=='b7e65e2dd7d82aa5c9957c2af7a192f475ed26f4140f3ab25ea18866bed53f01'"),
 ("new=(ROOT/'analysis/dev006/p8-native/libfs_utility_init-p8.elf').read_bytes()","new=(ROOT/'analysis/dev006/p9-safety-v2/libfs_utility_init-p9.elf').read_bytes()"),
 ("model=json.loads((ROOT/'analysis/dev006/p8-native/dataflow-audit.json').read_text())","model=json.loads((ROOT/'analysis/dev006/p9-safety-model-v3/result.json').read_text())"),
 ("'candidate':'HDD2TB-P8'","'candidate':'HDD2TB-P9'"),
 ("Expanded16384-slot native known-wrapper observer; P5 checker/storage behavior retained","Bounded checker array-growth failure/overread fix and calloc multiplication-overflow rejection; P8 storage/observer retained"),
 ("[Path(__file__),ROOT/'tools/build_hdd2tb_p1.py'","[Path(__file__),ROOT/'analysis/dev006/prepare_p9_safety_v2.py',ROOT/'analysis/dev006/p9-safety-v2/manifest.json',ROOT/'analysis/dev006/model_p9_safety.py',ROOT/'analysis/dev006/p9-safety-model-v3/result.json',ROOT/'analysis/dev006/p9-safety-delta/review.json',ROOT/'tools/build_hdd2tb_p1.py'"),
 ("ROOT/'candidates/HDD2TB-P8'","ROOT/'candidates/HDD2TB-P9'")]
for before,after in changes:
    assert before in text,before;text=text.replace(before,after)
with (R/'tools/build_hdd2tb_p9.py').open('x',encoding='utf8') as f:f.write(text)
with (R/'analysis/dev006/p9-builder-provenance.json').open('x',encoding='utf8') as f:
    json.dump({'source':'tools/build_hdd2tb_p8.py','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
       'destination':'tools/build_hdd2tb_p9.py','changes':changes,'prior_builder_modified':False},f,indent=2)
print('P9 packager prepared; prior builders unchanged.')
