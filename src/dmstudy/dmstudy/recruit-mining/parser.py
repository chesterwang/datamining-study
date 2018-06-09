#!/usr/bin/env python
# -*- coding:utf8 -*-

import urllib2
import BeautifulSoup
import os
import sys
import jieba
import nltk
import time
import HTMLParser

def search2file(city='北京',keywords='数据挖掘',outfile=os.getcwd()+'/data/search_list_page'):
	#convert the search list page into file

	#example parameter
	#searchurl = 'http://sou.zhaopin.com/jobs/searchresult.ashx?jl=北京&kw=数据挖掘&sm=0&p='
	search_url = 'http://sou.zhaopin.com/jobs/searchresult.ashx?jl=' + city + '&kw=' + keywords + '&sm=0&p='
	page_number = 2
	result_page_url = [ search_url + str(i+1) for i in range(page_number) ]
	page_htmlcontent = {}
	for page in result_page_url:
		#print '-----------------------' + str(datetime.datetime.now())
		print 'fetching ' + page + ' of ' + str(page_number) + ' pages'
		try:
			page_htmlcontent[page] = urllib2.urlopen(urllib2.Request(page)).read()
		except urllib2.URLError, e:
			print 'failed to fetch' + page
			raise MyException("There was an error： %r" % e)
		time.sleep(1)
	if os.path.isfile(outfile):
		print 'overwrite file: ' + outfile + ' with search result'
	f = open( outfile, 'w')
	f.write('\n\r'.join(page_htmlcontent.values()))
	f.close()

def parse_job_page(pageurl):
	#test page
	#pageurl = 'http://jobs.zhaopin.com/381640713250738.htm?ssidkey=y&ss=201&ff=03'

	#extract job description from job page
	
	print pageurl
	htmlcontent = urllib2.urlopen(urllib2.Request(pageurl)).read()

	try:
		soup = BeautifulSoup.BeautifulSoup(htmlcontent)
		requirementtag = soup.find('div',{'class': 'top-left'})
		descriptiontag = soup.find('div',{'class': 'terminalpage-content'})

		#remove comments
		comments  = descriptiontag.findAll(text=lambda text:isinstance(text, BeautifulSoup.Comment))
		[comment.extract() for comment in comments]

		#if requirementtag:
		#	jobcity = requirementtag.find('span',{'id':'positionCityCon'}).text
		if descriptiontag:
			#jobdescription = ' '.join([ para for para in descriptiontag.findAll(text=True)])
			#jobdescription = descriptiontag.findAll(text=True)
			jobdescription = ' '.join([ para for para in descriptiontag.findAll(text=True)])
			
			return jobdescription
	#other exception
	except HTMLParser.HTMLParseError:
		return u' ' 
	except UnicodeEncodeError:
		return u' ' 
	except AttributeError:
		return u' '

def text_cut_list(text):
	# cut text into list of word, and join list with comma ','

	#initial punc_marks
	punc_marks = [u',',u'.',u'，',u'。',u'(',u')',u'（',u'）',u'、',u':',u'-',u'：',u';',u'；',u'/',u' ',u'.',u'nbsp',u'&',u'\n']
	digits = map(str,str(range(10)))
	punc_marks.extend(digits)

	#remove punctuation marks
	for punc_mark in punc_marks:
		text = text.replace(punc_mark,u' ')

	#remove successive blank
	text = ' '.join(text.split())
	print text

	# cut description text
	cut_list = jieba.cut(text)
	#test code
	#print ','.join(cut_list)

	return cut_list

def job_url_extractor(job_tag):
	#extract job page url from html tag
	jobname_tag = job_tag.find('td',{'class': 'Jobname'})
	print jobname_tag.text
	job_url = jobname_tag.find('a').get('href')
	return job_url

def parse_search_list_page(search_list_page=os.getcwd()+'/data/search_list_page'):
	print 'reading search list page'
	content = open(search_list_page,'r').read()
	print 'parsing search list page'
	soup = BeautifulSoup.BeautifulSoup(content)
	job_tag_list = soup.findAll('table',{'class': 'search-result-tab'})
	return job_tag_list

def words_rank2file(job_description_list,outputfile=os.getcwd()+'/data/words_rank'):
	# computer frequency distribution of words, and sort according to occurence number
	words_list = [ job_description for job_description in job_description_list if job_description != u' ' ]
	freq_dist = nltk.FreqDist(words_list)
	words_rank = [ pair[0] + u'\t' + unicode(str(pair[1])) for pair in zip(freq_dist.keys(),freq_dist.values())]
	
	# ouput the words rank into file
	if os.path.isfile(outputfile):
		print 'overwrite file: ' + outputfile
	f = open( outputfile ,'w')
	f.write(u'\n'.join(words_rank).encode('utf-8'))
	f.close()
#----------------------------------------------------------------------
#make directory used for data and result 
result_dir = os.getcwd() + '/' + 'data'
if not os.path.exists(result_dir):
	os.mkdir(result_dir)

#transform search result into file
search2file(outfile=result_dir+'/search_list_page')

print 'reading search list page'
job_tag_list = parse_search_list_page(result_dir+'/search_list_page')

#extract job description
job_description_list = []
job_number = 0
for job_tag in job_tag_list:
	print '--------------------------------'
	job_number += 1
	if job_number ==3:
		break
	print 'parsing job ' + str(job_number)
	#extract job url
	job_url = job_url_extractor(job_tag)
	#parse job description
	job_description = parse_job_page(job_url)
	if job_description:
		pass
	else:
		print 'errorerrorerrorerrorerror'
		continue
	# add to final result list
	job_description_list.extend(text_cut_list(job_description))

words_rank2file(job_description_list)


