import json
#
#with open("answer_key.json", "r") as f:
#    answer_key = json.load(f)
#
#    print(answer_key['5da2351e42e60850385814c4'])
#total_tests = len(answer_key)
#
#print("Total tests:", total_tests)
output = {}
with open("test_ke.json", "r") as f:
    answer_key = json.load(f)
    for element in answer_key:
        test_name = element["test_name"]
        last_attempt_link = element["last_attempt_link"]
        output[test_name]=last_attempt_link
with open("test_key.json", "w") as f:
        json.dump(output, f, indent=4)