$sourceFolder = "../data-ingestion-server/"
$destFolder = "~/Documents/source/data-ingestion-server"
ssh jon@jon-zero-2-w-0 "pkill python && pkill fastapi"
rsync -r -e ssh --include="*/" --include="*.py" --exclude="*" $sourceFolder jon@jon-zero-2-w-0:$destFolder
rsync -r -e ssh --include="*/" --include="*.toml" --exclude="*" $sourceFolder jon@jon-zero-2-w-0:$destFolder
# scp $sourceFolder/*.toml jon@jon-zero-2-w-0:$destFolder/
ssh jon@jon-zero-2-w-0 "cd ${destFolder}/ && source .venv/bin/activate && nohup fastapi run ./main.py &"