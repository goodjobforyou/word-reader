# Grapheme groups. Commas separate independently playable phonemes.
PHONICS = '''stay|s~s;t~t;ay~eɪ
should|sh~ʃ;ou~ʊ;ld~d
flu|f~f;l~l;u~uː
else|e~e;l~l;se~s
exercise|e~e;x~k,s;er~ə;c~s;i~aɪ;se~z
enough|e~ɪ;n~n;ou~ʌ;gh~f
if|i~ɪ;f~f
habit|h~h;a~æ;b~b;i~ɪ;t~t
show|sh~ʃ;ow~əʊ
phone|ph~f;o…e~əʊ;n~n
then|th~ð;e~e;n~n
rest|r~r;e~e;s~s;t~t
take care of|t~t;a…e~eɪ;k~k;c~k;are~eə;o~ə;f~v
check|ch~tʃ;e~e;ck~k
less|l~l;e~e;ss~s
brush|b~b;r~r;u~ʌ;sh~ʃ
tooth|t~t;oo~uː;th~θ
twice|t~t;w~w;i…e~aɪ;c~s
hour|h~;our~aʊ,ə
free|f~f;r~r;ee~iː
hungry|h~h;u~ʌ;n~ŋ;g~ɡ;r~r;y~i
beef|b~b;ee~iː;f~f
ice cream|i…e~aɪ;c~s;c~k;r~r;ea~iː;m~m
little|l~l;i~ɪ;tt~t;le~ə,l
dumpling|d~d;u~ʌ;m~m;p~p;l~l;i~ɪ;ng~ŋ
tea|t~t;ea~iː
hamburger|h~h;a~æ;m~m;b~b;ur~ɜː;g~ɡ;er~ə
Mrs|Mrs~m,ɪ,s,ɪ,z
coconut|c~k;o~əʊ;c~k;o~ə;n~n;u~ʌ;t~t
interesting|i~ɪ;n~n;t~t;ere~r,ə;s~s;t~t;i~ɪ;ng~ŋ
seed|s~s;ee~iː;d~d
pull|p~p;u~ʊ;ll~l
stem|s~s;t~t;e~e;m~m
root|r~r;oo~uː;t~t
lotus|l~l;o~əʊ;t~t;u~ə;s~s
lake|l~l;a…e~eɪ;k~k
world|w~w;or~ɜː;l~l;d~d
round|r~r;ou~aʊ;n~n;d~d
different|d~d;i~ɪ;ff~f;ere~r,ə;n~n;t~t
way|w~w;ay~eɪ
river|r~r;i~ɪ;v~v;er~ə
nature|n~n;a~eɪ;t~tʃ;ure~ə
waterfall|w~w;a~ɔː;t~t;er~ə;f~f;a~ɔː;ll~l
forest|f~f;o~ɒ;r~r;e~ɪ;s~s;t~t
famous|f~f;a~eɪ;m~m;ou~ə;s~s
mountain|m~m;ou~aʊ;n~n;t~t;ai~ə;n~n
wind|w~w;i~ɪ;n~n;d~d
trip|t~t;r~r;i~ɪ;p~p
dangerous|d~d;a~eɪ;n~n;g~dʒ;e~ə;r~r;ou~ə;s~s
heavy|h~h;ea~e;v~v;y~i
hotel|h~h;o~əʊ;t~t;e~e;l~l
close|c~k;l~l;o…e~əʊ;s~z
umbrella|u~ʌ;m~m;b~b;r~r;e~e;ll~l;a~ə
raincoat|r~r;ai~eɪ;n~n;c~k;oa~əʊ;t~t
worry|w~w;o~ʌ;rr~r;y~i
fine|f~f;i…e~aɪ;n~n
fog|f~f;o~ɒ;g~ɡ
flood|f~f;l~l;oo~ʌ;d~d
fire|f~f;ire~aɪ,ə
know|kn~n;ow~əʊ
before|b~b;e~ɪ;f~f;ore~ɔː
go hiking|g~ɡ;o~əʊ;h~h;i~aɪ;k~k;i~ɪ;ng~ŋ
bring|b~b;r~r;i~ɪ;ng~ŋ'''
PHONICS = dict(line.split('|') for line in PHONICS.splitlines())
