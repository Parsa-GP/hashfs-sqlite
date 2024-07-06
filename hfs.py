from hashfs import HashFS
from io import StringIO
import argparse
import sqlite3
import os

parser = argparse.ArgumentParser(
	prog='HashFS CLI',
	description='A CLI for HashFS library in python.',)

# _ represents a single character	(? in wildcard)
# % represents any character		(* in wildcard)
# https://www.w3schools.com/sql/sql_like.asp
parser.add_argument('path', help='Path of objects')
parser.add_argument('-s', '--store', help='Store a file')
parser.add_argument('-g', '--get', help='Search and find a File with sql wildcards (_ and %) and throw the content to stdout')
parser.add_argument('-w', '--get_w_hash', help='Same as -g with hashid')
parser.add_argument('-d', '--delete', help='Removes a file')
parser.add_argument('-r', '--repair',  action='store_true', help='Repair the filesystem\'s Structure')
parser.add_argument('-l', '--list', action='store_true', help='List all files')
parser.add_argument('-i', '--info', action='store_true', help='Get Information about files/folders in the filesystem')


def store(fs, content, filename, extension=""):
	some_content = StringIO(content)
	address = fs.put(filename, extension)
	return {"hexid":address.id, "abspath":address.abspath, "relpath":address.relpath, "is_duplicate":address.is_duplicate}

def retrieve(fs, hashid="", abspath="", relpath=""):
	if hashid.strip():
		return fs.open(hashid)
	elif abspath.strip():
		return fs.open(abspath)
	elif relpath.strip():
		return fs.open(relpath)
	else:
		raise ValueError("None of the args is filled")

def remove(fs, hashid="", abspath="", relpath=""):
	if hashid.strip():
		return fs.delete(hashid)
	elif abspath.strip():
		return fs.delete(abspath)
	elif relpath.strip():
		return fs.delete(relpath)
	else:
		raise ValueError("None of the args is filled")

def repair(fs):
	#repaired = fs.repair(extensions=False)
	return fs.repair()

def walk_all(fs, nested_subfolders=False):
	""" Iterator """
	if nested_subfolders:
		return fs.files()
	else:
		return fs.folders() # ignore the nested subfolders

def conclusion(fs):
	return {"total_bytes":fs.size(), "file_count":fs.count()}


if __name__ == "__main__":
	hfs = HashFS(parser.parse_args().path, depth=4, width=3, algorithm='sha256')
	con = sqlite3.connect(os.path.join(parser.parse_args().path, "db.db"))
	cur = con.cursor()
	cur.execute("""CREATE TABLE IF NOT EXISTS "indexes" (
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


	if parser.parse_args().store:
		with open(parser.parse_args().store, encoding="utf-8") as f:
			info=store(hfs, f.read(), f.name)
		
		cur.execute(f"""INSERT INTO indexes (name, hash, category) VALUES ('{os.path.basename(f.name)}', '{info["hexid"]}', '');""")
		con.commit()
		print(f"Hex ID:           {info["hexid"]}\nAbsolute Path:    {info["abspath"]}\nReletive Path:    {info["relpath"]}\nFile Was Existed: {info["is_duplicate"]}")

	elif parser.parse_args().get:
		res = cur.execute(f"SELECT name,hash FROM indexes WHERE name LIKE '{parser.parse_args().get}'")
		print( "\n".join([f"{i[0]} ({i[1]})" for i in res.fetchall()]) )
		""" old method (exact filename)
			res = cur.execute(f"SELECT hash FROM indexes WHERE name='{parser.parse_args().get}';")
			try:
				h=res.fetchone()[0]
			except TypeError:
				exit("The File does not exists")
			with retrieve(hfs, hashid=h) as f:
				print(f.read().decode())"""

	elif parser.parse_args().get_w_hash:
		with retrieve(hfs, hashid=parser.parse_args().get_w_hash) as f:
			print(f.read().decode())		

	elif parser.parse_args().delete:
		remove(hfs, hashid=parser.parse_args().remove)

	elif parser.parse_args().repair:
		repair(hfs)

	elif parser.parse_args().list:
		#walk_all(hfs)
		res = cur.execute(f"SELECT name,hash FROM indexes WHERE category='' AND hide=0;")
		print( "\n".join([f"{i[0]} ({i[1]})" for i in res.fetchall()]) )

	elif parser.parse_args().info:
		info=conclusion(hfs)
		print(f"Bytes: {info['total_bytes']}\nCount: {info['file_count']}")
