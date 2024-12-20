# import json

# # Read the contents of the JSON file
# with open('json\setting.json', 'r') as file:
#     settings_data = json.load(file)

# # Fetch the value associated with the key "Mode"
# mode_value = settings_data.get("Mode", None)

# if mode_value:
#     print("Mode value:", mode_value)
# else:
#     print("Mode key not found in the settings.")
# import requests

# res1  = requests.put("http://localhost:2004/api/TestConfiguration/PutCertificationFilterToggle/V_2.0.1")
# res2  = requests.put("http://localhost:2004/api/TestConfiguration/PutCertificationFilterToggle/BPP")
# print(res1.status_code,res1.status_code)


# hex_string = "3F"
# decimal_value = int(hex_string, 16)
# print("Hexadecimal:", hex_string)
# print("Integer:", decimal_value)


l1 = ["0x31","0x00","0x00","0x03"]

l2 = list(int(res,16) for res in l1)

print(l2)