#!/usr/bin/env python3
# ============================================================================
#  Cho phep OpenSSL 3 bat tay TLS voi SQL Server doi cu (2008 / 2012 / 2014)
#
#  Loi khong co file nay:
#    [ODBC Driver 17 for SQL Server]SSL Provider:
#      [error:0A00014D:SSL routines::legacy sigalg disallowed or unsupported]
#    [error:0A000102:SSL routines::unsupported protocol]
#
#  Nguyen nhan: OpenSSL 3 mac dinh chan TLS < 1.2 va chan chu ky SHA1
#  (rsa_pkcs1_sha1) ma SQL Server doi cu van dung.
#
#  Script chuan hoa /etc/ssl/openssl.cnf:
#    openssl_conf -> [openssl_init] -> ssl_conf -> [ssl_sect]
#    -> system_default -> [system_default_sect]  (ghi de cau hinh legacy)
#  Lam theo cach nay thay vi "sed" vi moi ban Debian/Ubuntu de file khac nhau,
#  co ban khong he co san section [system_default_sect].
# ============================================================================
import re
import sys

CNF = sys.argv[1] if len(sys.argv) > 1 else "/etc/ssl/openssl.cnf"

LEGACY = """
[{ssl_sect}]
system_default = system_default_sect

[system_default_sect]
CipherString = DEFAULT:@SECLEVEL=0
MinProtocol = TLSv1
Options = UnsafeLegacyRenegotiation
SignatureAlgorithms = RSA+SHA1:ECDSA+SHA1:DSA+SHA1:RSA+SHA224:RSA+SHA256:RSA+SHA384:RSA+SHA512:ECDSA+SHA224:ECDSA+SHA256:ECDSA+SHA384:ECDSA+SHA512:RSA-PSS+SHA256:RSA-PSS+SHA384:RSA-PSS+SHA512
"""

s = open(CNF).read()

# 1. Phai co "openssl_conf = <section>" o dau file
if not re.search(r"^\s*openssl_conf\s*=", s, re.M):
    s = "openssl_conf = openssl_init\n" + s
init = re.search(r"^\s*openssl_conf\s*=\s*(\w+)", s, re.M).group(1)

# 2. Section [<init>] phai tro toi ssl_conf
if re.search(r"^\[\s*%s\s*\]" % init, s, re.M):
    if not re.search(r"^\s*ssl_conf\s*=", s, re.M):
        s = re.sub(r"^(\[\s*%s\s*\])" % init, r"\1\nssl_conf = ssl_sect",
                   s, count=1, flags=re.M)
else:
    s += "\n[%s]\nssl_conf = ssl_sect\n" % init
ssl_sect = re.search(r"^\s*ssl_conf\s*=\s*(\w+)", s, re.M).group(1)

# 3. Xoa cau hinh cu roi ghi de bang cau hinh legacy
for sec in (ssl_sect, "system_default_sect"):
    s = re.sub(r"^\[\s*%s\s*\].*?(?=^\[|\Z)" % sec, "", s, flags=re.M | re.S)
s = s.rstrip() + "\n" + LEGACY.format(ssl_sect=ssl_sect)

open(CNF, "w").write(s)
print("[fix-openssl-legacy] da cap nhat %s:" % CNF)
print(LEGACY.format(ssl_sect=ssl_sect).strip())
