import codecs

unicode_encoded_str = "\u0928\u092e\u0938\u094d\u0915\u093e\u0930, \u092e\u093e\u091d\u0902 \u0928\u093e\u0935 \u0905\u0935\u094d\u0935\u0932 \u0906\u0939\u0947."
decoded_str = codecs.decode(unicode_encoded_str, 'unicode_escape')

print(unicode_encoded_str.encode().decode('unicode-escape'))
