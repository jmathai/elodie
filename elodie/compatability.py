import os

def _decode(string, encoding='utf8'):
    if hasattr(string, 'decode'):
        return string.decode(encoding)

    return string


def _copyfile(src, dst):
    try:
        O_BINARY = os.O_BINARY
    except:
        O_BINARY = 0

    READ_FLAGS = os.O_RDONLY | O_BINARY
    WRITE_FLAGS = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | O_BINARY
    BUFFER_SIZE = 128*1024
        
    try:
        fin = os.open(src, READ_FLAGS)
        stat = os.fstat(fin)
        fout = os.open(dst, WRITE_FLAGS, stat.st_mode)
        for x in iter(lambda: os.read(fin, BUFFER_SIZE), ""):
            os.write(fout, x)
    finally:
        try: os.close(fin)
        except: pass
        try: os.close(fout)
        except: pass
        