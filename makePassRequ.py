import hashlib

password = input("password?")
salt = input("salt?")

gen = hashlib.sha512()
gen.update(password.encode() + salt.encode())

file = open("passRequ.txt", "w")
file.write(str((gen.hexdigest(), salt)))
file.close()
