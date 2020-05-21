#!/bin/bash
cp doc/logo.png build/d/land/

rm -f build/d/land/index.md
export pages=`find build/d/land -name *.md`

# create index
rm -f tmp.md
for f in $pages; do
    f2=${f:13:-3}
    f2=${f2//\//.}
    grep -h "^## \[.*" $f | sed -e"s/## \[\(.*\)\].*/* [\1]($f2#\1)/" >> tmp.md
done
echo % index >> build/d/land/index.md
cat tmp.md | sort >> build/d/land/index.md
rm tmp.md

export pages=`find build/d/land -name *.md | sort`

echo '<nav id="BAR">' > build/index
#echo '<h1>land</h1>' >> build/index
echo '<ul>' >> build/index
for f in $pages; do
    f2=${f:13:-3}
    f2=${f2//\//.}
    echo '<li><a href="'${f2}.html'">'${f2}'</a></li>' >> build/index
done
echo '</ul>' >> build/index
echo '</nav><nav id="MAIN">' >> build/index
echo -n "<br/><div id=\"FOOT\">Generated: " > build/date
date >> build/date
echo -n "</div>" >> build/date
for f in $pages; do
    f3=${f:13:-3}
    f2=build/d/land/${f3//\//.}
    pandoc $f --template=doc/pandoc_template.html -o $f2.html -B build/index -A build/date -c doc.css -H doc/doc.css
done
#cp build/d/land/land.html build/d/land/index.html
