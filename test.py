import base64

string = {'Dupa': {'Dupa': 1, 'Dupeczka': 'kurwa'}}

print('Pure string')
print(string)
print('Decoded string')

str_dec = base64.b64encode(string.encode('UTF-8')).decode('UTF-8')
print(str_dec)

print('Encoded string')
str_enc = base64.b64decode(str_dec).decode('UTF-8')
print(str_enc)