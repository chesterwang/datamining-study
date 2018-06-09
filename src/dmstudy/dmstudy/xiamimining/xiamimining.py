#!/bin/env python
#coding:utf-8

#generic music genre url: http://www.xiami.com/genre
#specific music genre url: http://www.xiami.com/genre/artists/gid/2


import tornado.httpclient as hc
from HTMLParser import HTMLParser
import time



def fetchpage(url):
	http_headers = {'User-Agent':'Firefox'}
	http_request = hc.HTTPRequest(url=url,headers=http_headers,method="GET",connect_timeout=20,request_timeout=20)
	http_client = hc.HTTPClient()

	http_response = http_client.fetch(http_request)

	return http_response.body

class GenreParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		#format genreitems [{genreid:,genrename:,},{},...,{} ]
		self.genrelist=[]
		self.flag = 0

	def handle_starttag(self, tag, attrs):
		#print "encounted the begining of a %s tag" % tag
		if tag == 'a':
			if attrs is None: 
				pass
			else:
				genreid=None
				title=None
				for key,value in attrs:
					if key=='href':
						index  = value.find("/genre/detail/gid/")
						if index > -1:
							genreid = value[index+len("/genre/detail/gid/"):]
						else:
							break
					if key=="title":
						genrename = value
				if genreid is not None and genrename is not None:
					self.genrelist.append({"genreid":genreid,"genrename":genrename})
					print genreid,genrename 

	def getgenrelist(self):
		return self.genrelist



class ArtistParser(HTMLParser):

	# parse this kind of file: http://www.xiami.com/genre/artists/gid/2
	def __init__(self):
		HTMLParser.__init__(self)
		#format genreitems [{artistid:,artistname:,},{},...,{} ]
		self.artistlist=[]
		self.flag = 0

	def handle_starttag(self, tag, attrs):
		#print "encounted the begining of a %s tag" % tag
		if tag == 'a':
			if attrs is None: 
				pass
			else:
				artistid=None
				title=None
				for key,value in attrs:
					if key=='href':
						index  = value.find("/artist/")
						if index > -1:
							artistid = value[index+len("/artist/"):]
						else:
							break
					if key=="title":
						title = value
				if artistid is not None and title is not None:
					self.artistlist.append({"artistid":artistid})
					self.flag=1

	def handle_data(self,data):
		if self.flag==1:
			self.artistlist[-1]["artistname"] = data
			self.flag=0
			print self.artistlist[-1]["artistid"],data

	def getartistlist(self):
		return self.artistlist

class ArtistInfoParser(HTMLParser):

	# parse this kind of file: http://www.xiami.com/artist/47821
		
	def __init__(self):
		HTMLParser.__init__(self)
		#format genreitems [{artistid:,artistname:,},{},...,{} ]
		self.artistinfos={}
		self.artistinfo={}
		self.flag = 0

	def handle_starttag(self, tag, attrs):
		#print "encounted the begining of a %s tag" % tag

		if tag == 'em':
			if attrs is None: 
				pass
			else:
				for key,value in attrs:
					if key=='id' and value=="play_count_num":
						self.artistinfo["index"]="play_count_num"
						self.flag=1
		if tag == 'a':
			if attrs is None: 
				pass
			else:
				hasflag=0
				for key,value in attrs:
					if  key == 'title' and value.find(u'位') > -1: hasflag=1
				if hasflag==1:
					for key,value in attrs:
						if key=='href' and (value.find("fans") > -1):
							# /artist/fans/id or artistname/fans 音乐人
							self.artistinfo["index"]="fans_num"
							self.flag=1

				for key,value in attrs:
					if key=='href' and value=="#wall":
						self.artistinfo["index"]="posts_num"
						self.flag=1

	def handle_data(self,data):
		if self.flag==1:
			self.artistinfo["number"] = data
			self.flag=0
			self.artistinfos[self.artistinfo["index"]] = self.artistinfo["number"]
			#print self.artistinfo["index"],self.artistinfo["number"]

	def getartistinfo(self):
		return self.artistinfos

if __name__ == "__main__":

	##fetch genre list 
	#http_content = fetchpage("http://www.xiami.com/genre")
	#http_content = http_content.decode('utf-8')
	#genre_parser = GenreParser()
	#genrelist = genre_parser.feed(http_content)
	#genrelist = genre_parser.getgenrelist()
	#genre_parser.close()

	##fetch artist list
	#fp = open("/home/chester/artists.txt",'w')
	#for genre in genrelist:
	#	genreid = genre["genreid"]
	#	#http://www.xiami.com/genre/artists/gid/2?spm=a1z1s.3057857.0.0.qdzKRU
	#	for pageno in range(1,22):
	#		http_content = fetchpage("http://www.xiami.com/genre/artists/gid/"+genreid+"/page/"+str(pageno))
	#		http_content = http_content.decode('utf-8')
	#		artist_parser = ArtistParser()
	#		artist_parser.feed(http_content)
	#		artistlist = artist_parser.getartistlist()
	#		artist_parser.close()
	#		for artist in artistlist:
	#			artist_line = genreid + ',"' + genre["genrename"] + '",' + artist["artistid"] + ',\"'+ artist["artistname"] + '\"\n'
	#			fp.write(artist_line.encode("utf-8"))
	#	time.sleep(3)
	#fp.close()

	#fetch artist information: include listening time, fans number, post number
	artistlist=[]
	fp = open("/home/chester/artists.txt",'r')
	fpinfo = open("/home/chester/artistsinfo.txt",'w')
	num = 0
	for line in fp.readlines():
		num+=1
		if num%50 == 0:
			time.sleep(3)
		artistidname = line.split(",")
		artistid = artistidname[2]
		print artistid
		#http://www.xiami.com/artist/47821
		http_content = fetchpage("http://www.xiami.com/artist/" + artistid)
		http_content = http_content.decode('utf-8')
		artist_info_parser = ArtistInfoParser()
		artist_info_parser.feed(http_content)
		artistinfo = artist_info_parser.getartistinfo()
		writeinfo =  ',' + artistinfo["play_count_num"]  + ',' + artistinfo["fans_num"] + ',' + artistinfo["posts_num"] + '\n'
		fpinfo.write(line[0:-1] + writeinfo.encode('utf-8'))
		print  line.decode('utf-8')[0:-1] + writeinfo
		artist_info_parser.close()
	fp.close()


