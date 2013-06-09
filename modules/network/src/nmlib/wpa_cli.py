from deepin_utils.process import get_command_output


def get_encry_table():
    command = ["/sbin/wpa_cli"]
    command.append("scan_results")
    wpa_output = map(lambda x: x.rstrip(), get_command_output(command))
    if not wpa_output:
        return {}
    striped = map(lambda l: l.split('\t'), wpa_output)[2:]
    table  = {}
    for line in striped:
        table[line[0]] =  line[3]
    return table

def get_encry_by_bssid(bssid):
    table = get_encry_table()
    if not table:
        print "cant get encry type, return wpa"
        return 'wpa-psk'
    else:
        try:
            encry = table[bssid]
            if "WPA" in encry:
                return "wpa-psk"
            elif "WEP" in encry:
                return "none"
            else:
                return ""
        except KeyError:
            return "wpa-psk"

print get_encry_by_bssid('6c:e8:73:2f:f9:8a')

