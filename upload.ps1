$BuildDir = ".\build\"
$DistDir = ".\dist\"
$EggInfoDir = ".\jsonify_html.egg-info\"

python setup.py sdist bdist_wheel
twine upload dist/*
Remove-Item -Recurse -Force -Path $BuildDir, $DistDir, $EggInfoDir