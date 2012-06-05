#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import string
import numpy as np
import csv

alaDebug=False
alaVersion='0.1 Beta'

alasurfaceFolder=""

surfaceListHeader=[] # Header from surface-list.csv
surfaceListData=[]   # Data from surface-list.csv
surfaceHeaders=[] # list of surface headers the actual grids
surfaceGrid=[] # The current surface grid

sampleOutOfBounds=[]

class AsciiGridHeaderClass(object):
    ncols=0
    nrows=0
    xllcorner=0
    yllcorner=0
    cellsize=0
    nodata_value=0
    xurcorner=0 # calculated later
    yurcorner=0 # calculated later
    surfacefolder=None
    surfacefile=None
    maxdecimals=0
    numwithdecimals=0
    numwithnodecimals=0
    
    def __init__(self,arg1,arg2):
        # no short names, must end in asc
        if len(arg2)<5:
            return
        # check if called .asc
        if len(arg2)-arg2.find('.asc')<>4:
            #print '^not ascii grid'
            return
            
        print "Loading header "+arg2
        #self.myvariable = 3
        self.ok=False
        
        try:
            self.f = open(arg1+arg2,"r")
        except IOError:
            print "Cannot open",arg1+arg2
            self.surfacefolder=None
            self.surfacefile=None
            return # was False
        
        self.cn=0 # row counter
        for self.row in self.f:
            
            if self.cn <= 5:
                self.row=self.row.rstrip() # could just be "\n"
                self.col=self.row.split(" ")
                self.title=self.col[0]
                self.value=self.col[len(self.col)-1]
                #print title, value
                if self.title=="ncols":
                    self.ncols=int(self.value)
                elif self.title=="nrows":
                    self.nrows=int(self.value)
                elif self.title=="xllcorner":
                   self.xllcorner=float(self.value)
                elif self.title=="yllcorner":
                    self.yllcorner=float(self.value)
                elif self.title=="cellsize":
                    self.cellsize=float(self.value)
                elif self.title=="NODATA_value":
                    self.nodata_value=self.value
                if self.cn==5:
                    if self.ncols==0 or self.nrows==0:
                        self.f.close()
                        self.surfacefolder=None
                        self.surfacefile=None
                        return
            else:
                break # only look at firts 6 rows, no need to lok at the data at this stage
                '''
                self.row=self.row.rstrip()
                self.col = self.row.split(" ")
                '''
            self.cn=self.cn+1
        self.f.close()
        
        self.surfacefolder=arg1
        self.surfacefile=arg2

        # works for Australia only grids, needs to be tidied up for elsewhere
        self.xurcorner = self.xllcorner + (self.ncols*(self.cellsize))
        self.yurcorner = self.yllcorner + (self.nrows*(self.cellsize))

        # work out number of decimals from middle row
        #self.numdecimals()'
        return

    def numdecimals(self):
        self.nd=0
        self.myrow=self.grid[int(self.nrows/2)]
        for self.s in self.myrow:
            self.l=len(self.s)
            self.i=self.s.find(".")
            if self.i>=0:
                if self.i==self.l-1:
                    self.nd=1
                else:
                    self.nd=self.l-self.i-1
                self.numwithdecimals=self.numwithdecimals+1
            else:
                self.numwithnodecimals=self.numwithnodecimals+1
            if self.nd>self.maxdecimals:
                self.maxdecimals=self.nd
        return
    
    def describe(self):
        print "------------------------------------------"
        print "Description of",self.surfacefile
        if self.surfacefile==None:
            return
        print "ncols:",self.ncols
        print "nrows:",self.nrows
        #print "maxdecimals:",self.maxdecimals
        #print "numwithdecimals:",self.numwithdecimals,"("+str(round(round(self.numwithdecimals)/round(self.ncols)*100.0,2))+"% n:"+str(self.ncols)+")"
        #print "numwithnodecimals:",self.numwithnodecimals,"("+str(round(round(self.numwithnodecimals)/round(self.ncols)*100.0,2))+"% n:"+str(self.ncols)+")"
        print "cellsize:",self.cellsize
        print "nodata_value:",self.nodata_value
        print "xllcorner:",self.xllcorner
        print "yllcorner:",self.yllcorner
        print "xurcorner:",self.xurcorner
        print "yurcorner:",self.yurcorner
        print "folder:",self.surfacefolder        
        #if myDebug:
        #    print "Here is row number",int(self.nrows/2),"(used to determine maxdecimals)"
        #    print self.grid[int(self.nrows/2)]
        return 

def loadSurfaceHeaders(suite,limit,test):
    global surfaceHeaders
    # Files can be commented out by placing a # as first chararter of file name
    # The surface list file should sit the the folder containing the ascii grids
    # It contains the ascii grid file names that you want to included in the test.
    # The surface list file is called surface-list.txt
    # only process if the suite of the layer is in the the desired list of suite(s).
    # if no 'Suite' column then load it anyway, up to limit.
    
    stpos=colpos(surfaceListHeader,['suite'])
    print 'Using column',stpos,'for suite'

    fpos=colpos(surfaceListHeader,['surface'])
    if fpos<0:
        fpos=0
    print 'Using column',fpos,'for filename'
    
    jpos=colpos(surfaceListHeader,['jackknife'])
    print 'Using column',jpos,'for jackknife'

    surfaceHeaders=[]
    cn=0
    for row in surfaceListData:
        print row
        fname=row[fpos]
        
        # check if in desired suite
        if stpos>0:
            suitevalue=[row[stpos]]
            if colpos(suite,suitevalue) < 0:
                continue
                
        # check if can be used for jackknife test        
        if jpos>=0 and test=='jackknife':
            if row[jpos]<>'yes':
                continue
        
        # check if is commented out
        if fname.find('#')==0:
            continue
            
        # check if below the debug limit
        if cn>=limit:
            continue

        # ---------------------------------
        
        print 'Loading',fname
        
        surfaceHeaders.append(AsciiGridHeaderClass(alasurfaceFolder,fname))
        if alaDebug:
            surfaceHeaders[cn].describe()
            
        cn+=1
        
    #print len(surfaceHeaders),'surface headers loaded'

def loadSurfaceList(surfaceFolder):
    global surfaceListHeader
    global surfaceListData
    global alasurfaceFolder
    
    alasurfaceFolder=surfaceFolder
    
    surfaceListHeader=[]
    surfaceListData=[]
    
    print "Loading surface-list.csv"
    cn=0
    f=open(surfaceFolder+'surface-list.csv','rb')    
    reader = csv.reader(f)
    for row in reader:
        if cn==0:
            for s in row:
                if len(s)>0:
                    surfaceListHeader.append(s.strip().lower())
        else:
            if len(row) >0:
                # pad row with '' entries if necessary
                # then get rid of extra data columns
                while len(row)<len(surfaceListHeader):
                    row.append('')
                while len(row)>len(surfaceListHeader):
                    row.delete(len(row)-1)
                surfaceListData.append(row)
        cn+=1
    f.close()
    print "In loadSurfaceList() add check that headers are on"
    
def getSurfaceValues(h):
    a=[]
    print h.surfacefile
    print "ncols:",h.ncols
    print "nrows:",h.nrows
    cn=0
    for x in range(h.ncols):
        for y in range(h.nrows):
                    v=surfaceGrid[y][x]
                    if v<>h.nodata_value:
                        a.append(float(v))
        
    return np.array(a)
    
def getSurfaceValuesAsString(h):
    a=[]
    print h.surfacefile #,'No data value:',h.nodata_value,'len(surfaceGrid)',len(surfaceGrid)
    print "ncols:",h.ncols
    print "nrows:",h.nrows
    for x in range(h.ncols):
        for y in range(h.nrows):
            v=surfaceGrid[y][x]
            if v<>h.nodata_value:
                a.append(v)
    return np.array(a)
    
def loadSurfaceGrid(folder,fname):
    global surfaceGrid
    
    #data = [line.strip().split() for line in open("data.txt")]
    #print data[0][0] #first row, first col
    #print data[1][0] #second row, first col

    surfaceGrid=[]
    print 'Loading',fname
    
    try:
        f = open(folder+fname,"r")
    except IOError:
        print "Cannot open",folder+fname
        return # was False
        
    cn=0 #row counter
    for row in f:
        if cn >=6:
            line=row.rstrip()
            col = line.split(" ")
            a=[]
            for v in col:
                if len(v)>0: # ignore nulls caused by multiple spaces
                    a.append(v)
            surfaceGrid.append(a)
        cn=cn+1
    f.close()
    
def findHeader(name):
    for h in surfaceHeaders:
        if h.surfacefile==name:
            return h
    return None

def readAsciiGrid(lat,lon,h,g):
    # h is header, g is grid
    # Works for australia only
    inside=True

    x = int((lon-h.xllcorner)/h.cellsize)
    y = (h.nrows-1)-int((lat-h.yllcorner)/h.cellsize)
    
    value=None
    if (x >= 0 and x <= h.ncols) and (y>=0 and y<h.nrows):
        value=g[y][x]
        if value==h.nodata_value:
            value=None
    else:
        inside=False
        
    if alaDebug:
        print "readAsciiGrid lat,y,lon,x,value,withingrid",lat,y,lon,x,value,inside
        
    return value

def scanSpecies(filename,h,g,fi,s):
    # h is surface header, g is surfacegrid,  s is the particular suite value
    global sampleOutOfBounds
    isInt=(fi=='int') # whether to load as int
    a=[]
    f = open(filename,"r")
    cn=0
    header=[]
    for row in f:
        if cn==0:
            if alaDebug:
                print "header=",row
            
            header=row.strip().split(",")
            
            # Check for latitude    
            ypos=colpos(header,['decimallatitude','y','latitude','lat'])
            if ypos<0:
                print 'ERROR: Cannot find decimalLatitude (or equivalent) in', filename
                break
                
            # Check for longitude
            xpos=colpos(header,['decimallongitude','x','longitude','long','lon'])
            if xpos<0:
                print 'ERROR: Cannot find decimalLongitude (or equivalent) in', filename
                break
            
            # Check for names
            spos=colpos(header,['scientificname'])
            vpos=colpos(header,['vernacularname','species'])
                
        else:
            e=row.strip().split(",")
            
            # work out species name
            if spos>=0:
                species=e[spos]
            elif vpos>=0:
                species=e[vpos]
            else:
                species=filename.split(".")[0]
            
            lon=float(e[xpos])
            lat=float(e[ypos])
            v=readAsciiGrid(lat,lon,h,g)
            
            if alaDebug:
                print lat,lon,v,cn
                
            if v <> None:
                if isInt:
                    v=int(v)
                else:
                    v=float(v)
                a.append((v,lon,lat,cn))
            else:
                sampleOutOfBounds.append((e[1],e[2],cn,h.surfacefile,s))
                #print "ERROR:",filename,h.surfacefile,s,lon,lat,'is out of bounds of',h.surfacefile
        cn=cn+1
    f.close()
    
    if len(sampleOutOfBounds)>0:
        print 'ERROR: ',len(sampleOutOfBounds),'records are out of bounds.'
    
    if isInt:
        return np.array(a,dtype=[('value', int),('lon', float), ('lat', float),('id', int)]) # http://docs.scipy.org/doc/numpy/user/basics.rec.html
    else:
        return np.array(a,dtype=[('value', float),('lon', float), ('lat', float),('id', int)]) # http://docs.scipy.org/doc/numpy/user/basics.rec.html

def about():
    print "ALA Tools Version:",alaVersion
    
def colpos(columns,values): # both lists, values must be lower case, columns are converted to lower case
    pos=-1
    for v in values:
        for i,c in enumerate(columns):
            if c.lower()==v:
                pos=i
                break
        if pos <> -1:
            break
    return pos

def getOccurrences(filename):

    a=[]
    f = open(filename,"r")
    header=[]
    for row in f:
        if len(header)==0:
  
            header=row.strip().split(",")
            
            # Check for latitude    
            ypos=colpos(header,['decimallatitude','y','latitude','lat'])
            if ypos<0:
                print 'ERROR: Cannot find decimalLatitude (or equivalent) in', filename
                break
                
            # Check for longitude
            xpos=colpos(header,['decimallongitude','x','longitude','long','lon'])
            if xpos<0:
                print 'ERROR: Cannot find decimalLongitude (or equivalent) in', filename
                break
            
            # Check for names
            spos=colpos(header,['scientificname'])
            vpos=colpos(header,['vernacularname','species'])
                
        else:
            e=row.strip().split(",")
            
            # work out species name
            if spos>=0:
                species=e[spos]
            elif vpos>=0:
                species=e[vpos]
            else:
                species=filename.split(".")[0]
            
            lon=float(e[xpos]) #was float(e[xpos])
            lat=float(e[ypos]) #was float(e[ypos])
            a.append([lon,lat]) # was a.append((lon,lat))
    f.close()

    return np.array(a)

def removeDuplicateCoordinates(folder,filename,outfile,numdecimals):   
    print "Removing duplicate lat longs in",filename
    
    print "Numdecimals",numdecimals
    
    if numdecimals>=0.0:
        print "and generalising coordinates ",numdecimals,' decimal places'
    
    f = open(folder+filename,"r")
    # header=""
    cn=0
    d=[]
    header=[]
    for row in f:
        if cn==0:
            header=row.strip().split(",")
            
            # Check for latitude    
            ypos=colpos(header,['decimallatitude','y','latitude','lat'])
            if ypos<0:
                print 'ERROR: Cannot find decimalLatitude (or equivalent) in', filename
                break
                
            # Check for longitude
            xpos=colpos(header,['decimallongitude','x','longitude','long','lon'])
            if xpos<0:
                print 'ERROR: Cannot find decimalLongitude (or equivalent) in', filename
                break
            
            # Check for names
            spos=colpos(header,['scientificname'])
            vpos=colpos(header,['vernacularname','species'])
                
        else:
            e=row.strip().split(",")
            
            # work out species name
            if spos>=0:
                species=e[spos]
            elif vpos>=0:
                species=e[vpos]
            else:
                species=filename.split(".")[0]
             
            # work out coordinates
            lon=e[xpos]
            lat=e[ypos]
            
            if numdecimals>=0.0:
                xs=str(round(float(lon),numdecimals))
                ys=str(round(float(lat),numdecimals))
            else:
                xs=lon
                ys=lat
            if alaDebug:
                print lon,lat,xs,ys
            d.append([species+","+xs+","+ys])
        cn=cn+1
    f.close()

    d2=np.unique(np.array(d))
    #print d2
    
    f = open(folder+outfile,"w")
    
    '''
    if maxentColumns:
        f.write('species,longitude,latitude'+'\n')
    elif len(header)>0:
        if spos>=0:
            s='scientificName,decimalLongitude,decimalLatitude'
        else:
            s='vernacularName,decimalLongitude,decimalLatitude'
        f.write(s+'\n')
    '''
    
    f.write('species,x,y'+'\n')

    for s in d2:
        f.write(s+'\n')
    f.close()
    print "Started with",cn,"occurrences now have",d2.size,"occurrences"
    print "Data written to no-duplicate-data.csv"
    return
