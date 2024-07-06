""" CLI For HashFS """
from argparse import ArgumentParser
from sqlite3 import connect
from os import path
from sys import exit as sysexit
from hashfs import HashFS

# pylint: disable=W0611

parser = ArgumentParser(
	prog='HashFS CLI',
	description='A CLI for HashFS library in python.',)

# _ represents a single character	(? in wildcard)
# % represents any character		(* in wildcard)
# https://www.w3schools.com/sql/sql_like.asp
parser.add_argument('path', help='Path of filesystem folder')
parser.add_argument('-s', '--store', help='Store a file')
parser.add_argument('-g', '--get', help='Search and find a File with sql wildcards (_ and %) and t \
hrow the content to stdout')
parser.add_argument('-w', '--get_w_hash', help='Same as -g with hashid')
parser.add_argument('-d', '--delete', help='Removes a file with sql wildcards')
parser.add_argument('-r', '--repair', action='store_true',help='Repair the filesystem\'s Structure')
parser.add_argument('-l', '--list', action='store_true', help='List all files')
parser.add_argument('-i', '--info', action='store_true', help='Get Information about files/folders \
in the filesystem')


def store(fs, filename, extension=""):
	""" Store a file in fs """
	#some_content = StringIO(content)
	address = fs.put(filename, extension)
	return {"hexid":address.id, "abspath":address.abspath, "relpath":address.relpath, "is_duplicat \
e":address.is_duplicate}

def retrieve(fs, hashid="", abspath="", relpath=""):
	""" Get the content of given file """
	if hashid.strip():
		return fs.open(hashid)
	if abspath.strip():
		return fs.open(abspath)
	if relpath.strip():
		return fs.open(relpath)
	raise ValueError("None of the args is filled")

def remove(fs, hashid="", abspath="", relpath=""):
	""" Removes a file from the given fs """
	if hashid.strip():
		return fs.delete(hashid)
	if abspath.strip():
		return fs.delete(abspath)
	if relpath.strip():
		return fs.delete(relpath)
	raise ValueError("None of the args is filled")

def repair(fs):
	""" Repair the fs """
	#fs.repair(extensions=False)
	return fs.repair()

def walk_all(fs, nested_subfolders=False):
	""" Iterator """
	if nested_subfolders:
		return fs.files()
	else:
		return fs.folders() # ignore the nested subfolders

def conclusion(fs):
	""" Get Information about database and filesystem """
	return {"total_bytes":fs.size(), "file_count":fs.count()}


if __name__ == "__main__":
	hfs = HashFS(parser.parse_args().path, depth=4, width=3, algorithm='sha256')
	con = connect(path.join(parser.parse_args().path, "db.db"))
	cur = con.cursor()
	cur.execute("""CREATE TABLE IF NOT EXISTS indexes (
		"id"	INTEGER,
		"name"	TEXT NOT NULL UNIQUE,
		"hash"	TEXT NOT NULL,
		"category"	TEXT,
		"hide"	INTEGER NOT NULL DEFAULT 0,
		PRIMARY KEY("id" AUTOINCREMENT)
		);""")
	cur.execute("""CREATE TABLE IF NOT EXISTS cats (
		"id"	INTEGER,
		"catname"	TEXT NOT NULL UNIQUE,
		"description"	TEXT,
		PRIMARY KEY("id" AUTOINCREMENT)
		);""")

	if path.isfile(parser.parse_args().path):
		with open(parser.parse_args().path, encoding="utf-8") as f:
			info=store(hfs, f.read(), f.name)

		cur.execute(f"""INSERT INTO indexes (name, hash, category) VALUES ('{path.basename(f.name) \
}', '{info["hexid"]}', '');""")
		con.commit()
		print(f"Hex ID:           {info["hexid"]}\nAbsolute Path:    {info["abspath"]}\nReletive Pa \
th:    {info["relpath"]}\nFile Was Existed: {info["is_duplicate"]}")


	elif parser.parse_args().store:
		with open(parser.parse_args().store, encoding="utf-8") as f:
			info=store(hfs, f.read(), f.name)

		cur.execute(f"""INSERT INTO indexes (name, hash, category) VALUES ('{path.basename(f.name)} \
', '{info["hexid"]}', '');""")
		con.commit()
		print(f"Hex ID:           {info["hexid"]}\nAbsolute Path:    {info["abspath"]}\nReletive Pa \
th:    {info["relpath"]}\nFile Was Existed: {info["is_duplicate"]}")

	elif parser.parse_args().get:
		res = cur.execute(f"SELECT name,hash FROM indexes WHERE name LIKE '{parser.parse_args().get}'")
		print( "\n".join([f"{i[0]} ({i[1]})" for i in res.fetchall()]) )

		# old method (exact filename)
		#res = cur.execute(f"SELECT hash FROM indexes WHERE name='{parser.parse_args().get}';")
		#try:
		#	h=res.fetchone()[0]
		#except TypeError:
		#	sysexit("The File does not exists")
		#with retrieve(hfs, hashid=h) as f:
		#	print(f.read().decode())"""

	elif parser.parse_args().get_w_hash:
		with retrieve(hfs, hashid=parser.parse_args().get_w_hash) as f:
			print(f.read().decode())

	elif parser.parse_args().delete:
		res = cur.execute(f"SELECT hash FROM indexes WHERE name LIKE '{parser.parse_args().delete}';")
		try:
			h=res.fetchone()[0]
		except TypeError:
			sysexit("The File does not exists")
		remove(hfs, hashid=h)

	elif parser.parse_args().repair:
		repair(hfs)
		print("The fs has been repaired.")

	elif parser.parse_args().list:
		# List the fs files: `walk_all(hfs)` (returns iterator)
		res = cur.execute("SELECT name,hash FROM indexes WHERE category='' AND hide=0;")
		print( "\n".join([f"{i[0]} ({i[1]})" for i in res.fetchall()]) )

	elif parser.parse_args().info:
		info=conclusion(hfs)
		print(f"Bytes: {info['total_bytes']}\nCount: {info['file_count']}")
