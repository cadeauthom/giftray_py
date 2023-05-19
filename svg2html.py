import os
import glob

def recursive_dir_search_svg(directory):
    out = ""
    files = glob.glob(directory+"/*.svg")
    if files:
      out+="<details><summary>"+directory+"</summary><ul>\n"
      for f in files:
        out+="<li><img src="+f+"/> <span>"+os.path.basename(f)+"</span>\n"
      out+="</ul></details>\n"
    dirs = glob.glob(directory+"/*")
    for d in dirs:
      if os.path.isdir(d):
        a=recursive_dir_search_svg(d)
        if a:
          out+=a
    return out

end ='''
</body>
</html>'''
start='''
<!doctype html>
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<title>GifTray Images</title>
		<style type="text/css">
			ul li {list-style: none; margin-bottom: 15px;}
			ul li img {display: inline; width:20px; height:20px;}
			ul li span {display: inline ;}
		</style>
	</head>
	<body>'''
print(start)
print(recursive_dir_search_svg("svg"))
print(end)
