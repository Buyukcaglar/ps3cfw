"""Minimal FTP client for webMAN MOD on the console (anonymous, binary).

Each read opens its own login: webMAN handles an aborted RETR poorly, and a
fresh session per slice is what the 2026-10-18 persistence reader used
successfully (167 logins, 212 s for ~120 MB).
"""
import ftplib
import hashlib
import socket

CHUNK = 1 << 16


class Console:
    def __init__(self, host, port=21, timeout=60):
        self.host, self.port, self.timeout = host, port, timeout

    def _login(self):
        f = ftplib.FTP()
        f.connect(self.host, self.port, timeout=self.timeout)
        f.login('anonymous', 'anonymous@')
        f.voidcmd('TYPE I')
        return f

    def size(self, path):
        """Remote size in bytes, or None when the path does not exist."""
        f = self._login()
        try:
            return f.size(path)
        except ftplib.error_perm:
            return None
        finally:
            f.close()

    def read(self, path, offset=0, length=None, keep=False):
        """Read `length` bytes at `offset` (whole file when None).

        Returns dict(bytes, sha256, eof, data?). `eof` is True when the server
        ended the stream right after the requested range.
        """
        f = self._login()
        h, got, parts = hashlib.sha256(), 0, []
        try:
            conn = f.transfercmd('RETR ' + path, rest=offset or None)
            try:
                while length is None or got < length:
                    want = CHUNK if length is None else min(CHUNK, length - got)
                    chunk = conn.recv(want)
                    if not chunk:
                        break
                    h.update(chunk)
                    got += len(chunk)
                    if keep:
                        parts.append(chunk)
                if length is None or got < length:
                    eof = True
                else:
                    conn.settimeout(5)
                    try:
                        eof = conn.recv(1) == b''
                    except socket.timeout:
                        eof = False
            finally:
                conn.close()
            if eof:
                try:
                    f.voidresp()
                except ftplib.all_errors:
                    pass
        finally:
            f.close()  # no QUIT: an aborted transfer can leave the reply stream unusable
        out = {'bytes': got, 'sha256': h.hexdigest(), 'eof': eof}
        if keep:
            out['data'] = b''.join(parts)
        return out

    def rename(self, src, dst):
        f = self._login()
        try:
            f.rename(src, dst)
        finally:
            f.close()

    def delete(self, path):
        f = self._login()
        try:
            f.delete(path)
        finally:
            f.close()

    def names(self, directory):
        f = self._login()
        try:
            return [n.rsplit('/', 1)[-1] for n in f.nlst(directory)]
        except ftplib.error_perm:
            return []
        finally:
            f.close()
