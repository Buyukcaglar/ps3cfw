"""Create a new receipt-only recorder; preserve all prior writers unchanged."""
import hashlib
import json
from pathlib import Path

R=Path(__file__).resolve().parents[2]


def main():
    parent=R/'analysis/dev006/record_p11_staging.py'
    source=parent.read_text('utf8')
    changes=[('P11','P12'),('p11-review','p12-review'),('record_p11_staging.py','record_p12_staging.py'),
        ('HW002AD','HW002AF'),('HW002AA','OLDER_CONTROL_SCOPE'),('HW002AC','HW002AE'),
        ('OLDER_CONTROL_SCOPE','HW002AC'),('P10','P11'),
        ('d299aad533a12ff8a7a6e5bc0e20093977de18e7e9eef0aac7cc58b4aa065552','7fb5d6e57ef53654f336745dbc9463c8e6b2cded03b05cdbeb80e5125215fb7c'),
        ('78423','78455'),('b5e140fe5ce114e2b25924b30cfb77b6cb956741ff45f91ccd0a1adf873932b6','eb38afbb59179553ba3055d19727770b90bfec6b1111326345a4bd01644736bc')]
    for old,new in changes:source=source.replace(old,new)
    source=source.replace("paths=set(old['bindings'])|{'analysis/dev006/record_p12_staging.py',",
        "paths=set(old['bindings'])|{'analysis/dev006/record_p12_staging.py', 'analysis/dev006/prepare_p12_staging_recorder.py',")
    target=R/'analysis/dev006/record_p12_staging.py'
    with target.open('x',encoding='utf8') as stream:stream.write(source)
    with (R/'analysis/p12-review/staging-recorder-provenance.json').open('x',encoding='utf8') as stream:
        json.dump({'parent':'analysis/dev006/record_p11_staging.py','parent_sha256':hashlib.sha256(parent.read_bytes()).hexdigest(),
            'new_recorder_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'changes':changes,
            'parent_modified':False,'firmware_F_read_or_backup':False},stream,indent=2);stream.write('\n')
    # Bind the source custody file in the recorder's new checkpoint too.
    source=target.read_text('utf8').replace("'analysis/p12-review/usb-staging-receipt.json',",
        "'analysis/p12-review/usb-staging-receipt.json', 'analysis/p12-review/staging-recorder-provenance.json',")
    target.write_text(source,encoding='utf8')
    # The provenance first hash intentionally records the pre-binding generated source;
    # final source hash is sealed by the completed staging checkpoint.
    print('New P12 receipt recorder prepared; no USB operation performed here.')


if __name__=='__main__':main()
