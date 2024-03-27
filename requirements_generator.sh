pip list | grep 'pipreqs' || pip install pipreqs

pipreqs --force --ignore example,test .
