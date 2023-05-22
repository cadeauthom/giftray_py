import os
import sys
import getopt
import glob

def recursive_dir_search_svg(directory):
    out = ""
    files = glob.glob(directory+"/*.svg")
    c=0
    m=6
    if files:
      out+="<details><summary>"+directory+"</summary><table><tr>\n"
      for f in files:
        out+="<th><img src="+f+"/> <span>"+os.path.basename(f)+"</span></th>\n"
        c+=1
        if c == m:
            out+="</tr><tr>\n"
            c=0
      if c != 0:
        out+="</tr>\n"
      out+="</table></details>\n"
    dirs = glob.glob(directory+"/*")
    for d in dirs:
      if os.path.isdir(d):
        a=recursive_dir_search_svg(d)
        if a:
          out+=a
    return out

def help():
    print("Error in arguments: [--out=<output file>] [-dir=<directoty to explore>]")
    exit(1)

out=''
directory='.'
argv = sys.argv[1:]
try:
    options, args = getopt.getopt(argv, "o:d:",
                               ["out=",
                                "dir=","directory="])
except:
    help()

for name, value in options:
    if name in ['-o', '--out']:
        out = value
    elif name in ['-d', '--dir', '--directory']:
        directory = value

if not os.path.exists(directory) or not os.path.isdir(directory):
    print(directory+' is not a valid directory to be explored')
    help()

if out:
    file_name, file_extension = os.path.splitext(out)
    file_dir = os.path.dirname(file_name)
    if not file_extension:
        out = out + '.html'
    elif file_extension != '.html':
        print(out+' must be an html file')
        exit(2)
    elif not file_dir:
        pass
    else:
        print(out+' must be without directory definiton')
        help()

end ='''
</body>
</html>'''
start='''
<!doctype html>
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<title>GifTray Images</title>
		<style type="text/css">
			table tr th {}
			table tr th img {display: inline; width:20px; height:20px;}
			table tr th span {display: inline ;}
		</style>
	</head>
	<body>'''

if out:
    fout=open(out,'w')
else:
    fout=sys.stdout
fout.write(start)
fout.write(recursive_dir_search_svg(directory))
fout.write(end)
if out:
    fout.close
