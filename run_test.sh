export PYTHONPATH=.:$PYTHONPATH

pytest -v test/memory_test/unit_test_client.py
# pytest -v test/memory_test/unit_test_BMM_Milvus.py
# pytest -v test/memory_test/unit_test_BMM_mongoDB.py
# pytest -v test/memory_test/unit_test_BAS.py

