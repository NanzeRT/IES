from matplotlib import pyplot as plt

"""
sun = '''-0,100936457293854
0,346783922865246
-0,0601266754971028
-0,406235766749175
0,435106917347448
-0,237900619779573
-0,0876696383008575
0,426971304446596
0,151636663480479
-0,0425712672759593
0,381893235757707
0,421857279088057
0,61914793988838
1,01544596882286
1,71812137767937
2,25699150283726
2,99475187227041
3,442718692886
4,02837101317448
5,53831912304168
6,09480180211355
7,06683976145345
7,68624494406493
9,13780300820097
9,96858746534943
10,0193818827281
11,4209938384863
12,2818370804975
12,263135687427
12,8328564857826
12,4363459197821
12,8344732797685
12,7853425784934
12,6766380245053
12,7770775110921
11,3122113432093
10,2754678235966
9,29100479933168
8,34874852205096
7,88647847453443
7,01400267628313
6,46803588584539
5,40524272099991
4,48333416024874
3,52043059759463
2,25825316679491
1,00380240911054
0,40096901294676
-0,313133606691831
0,0153612718148083
0,334319255178859
-0,459411171763371
-0,140509165577489
0,00550671056401275
-0,323272139429302
0,0287534033256793
0,315430725438077
0,185946530306494
0,324718364827207
0,261095735135893
0,887937520308844
1,21778521876415
2,60159936810563
2,97669686372654
3,13769044911572
4,16134695954462
4,30601293256548
5,74241609912164
6,47131424209837
6,80734261194837
7,98354845316258
9,52871781255467
9,46823809974369
10,8351768524422
12,2013076570795
12,8550013772913
13,5459445538604
13,2501800802645
13,6230593219839
13,3002277568762
13,95848548481
13,3224668944219
12,4463813136675
11,3671070312691
10,4849587678983
9,59465756193459
8,89369151539511
8,19999259507287
7,86782336704823
6,61883626004008
5,5156614480453
4,66976520155989
4,19528854822052
1,40801148813113
1,23275917679033
0,59170806290354
0,489817620539382
-0,483281086930105
0,463827307803238
0,390004398438161
0
'''
s2 = '''0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0,4833984375
2,109375
2,4755859375
3,4716796875
4,04296875
5,537109375
6,2841796875
6,2841796875
7,529296875
8,203125
8,203125
8,7744140625
8,3935546875
8,701171875
8,701171875
8,525390625
8,701171875
7,4560546875
6,4013671875
5,4638671875
4,716796875
4,16015625
3,3544921875
2,7978515625
1,728515625
0,732421875
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0,4248046875
0,615234375
2,05078125
2,607421875
3,046875
4,16015625
5,654296875
5,4638671875
6,708984375
7,9541015625
8,4521484375
9,140625
8,8330078125
9,140625
8,9501953125
9,4482421875
8,9501953125
8,0859375
7,20703125
6,3427734375
5,654296875
4,9072265625
4,3505859375
3,9697265625
2,7978515625
1,8017578125
0,8056640625
0,4248046875
0
0
0
0
0
0
0
0
'''
"""

"""
sun = '''-0,100936457293854
0,346783922865246
-0,0601266754971028
-0,406235766749175
0,435106917347448
-0,237900619779573
-0,0876696383008575
0,426971304446596
0,151636663480479
-0,0425712672759593
0,381893235757707
0,421857279088057
0,613838095798841
1,01710402646733
1,69020551522195
2,28012474074287
3,0051802970374
3,44036719263667
4,0092631811833
5,53134670624286
6,11012647137793
7,04389273912449
7,70561415519165
9,11901325994378
9,95447254655361
10,0317537114668
11,4254680309132
12,2733694878099
12,2821172152697
12,8231726541915
12,45234398457
12,8152412267787
12,8073499666818
12,6798413930933
12,7691248057838
11,3226721370812
10,4780322943627
9,55952687026906
8,69917463036008
8,30395893919105
7,45709369797932
6,89584468859356
5,77446613804301
4,73984204684916
3,7296693519047
2,33955747138043
1,03797322601538
0,393995225110537
-0,313133606691831
0,0153612718148083
0,334319255178859
-0,459411171763371
-0,140509165577489
0,00550671056401275
-0,323272139429302
0,0287534033256793
0,315430725438077
0,185946530306494
0,324718364827207
0,261095735135893
0,893826990599874
1,15461601882231
2,50413730606522
2,84734431626234
2,92579541786446
3,89734152899888
3,99966336639725
5,40208842062274
6,13558824651502
6,53536620995076
7,75041469409203
9,35802700412211
9,26915251736991
10,5277151548496
11,7334023655478
12,2388402410764
12,7373389255184
12,3111049503131
12,6793679366281
12,4956582165158
13,2924367296868
12,7891351108858
12,0769637304018
11,1376166094701
10,302623594405
9,31770787764564
8,54798648529227
7,78138339024316
7,41567768402507
6,19643282801022
5,1267114504003
4,40237026179274
3,98027505314497
1,34676951984201
1,18163367779434
0,584148560641762
0,489817620539382
-0,483281086930105
0,463827307803238
0,390004398438161
0
'''
s2 = '''0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
1,23046875
1,8017578125
2,607421875
3,4130859375
4,716796875
5,4638671875
5,4638671875
6,708984375
7,3974609375
7,3974609375
7,8955078125
7,587890625
7,8955078125
7,8955078125
7,705078125
7,8955078125
6,650390625
5,7861328125
5,09765625
4,16015625
3,9111328125
2,9736328125
2,4169921875
1,4208984375
0,4248046875
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0,9814453125
1,8017578125
2,2265625
3,3544921875
4,8486328125
4,658203125
5,9619140625
7,03125
7,3974609375
7,8955078125
7,529296875
7,705078125
7,529296875
8,203125
7,8369140625
7,1484375
6,4599609375
5,7861328125
4,8486328125
4,1015625
3,3544921875
2,9736328125
1,8017578125
0,8056640625
0
0
0
0
0
0
0
0
0
0
'''
"""


sun = '''-0,100936457293854
0,346783922865246
-0,0601266754971028
-0,406235766749175
0,435106917347448
-0,237900619779573
-0,0876696383008575
0,426971304446596
0,151636663480479
-0,0425712672759593
0,381893235757707
0,421857279088057
0,613838095798841
1,01710402646733
1,69020551522195
2,28012474074287
3,0051802970374
3,44036719263667
4,0092631811833
5,53134670624286
6,11012647137793
7,04389273912449
7,70561415519165
9,11901325994378
9,95447254655361
10,0317537114668
11,4254680309132
12,2733694878099
12,2821172152697
12,8231726541915
12,45234398457
12,8152412267787
12,8073499666818
12,6798413930933
12,7691248057838
11,3226721370812
10,4780322943627
9,55952687026906
8,69917463036008
8,30395893919105
7,45709369797932
6,89584468859356
5,77446613804301
4,73984204684916
3,7296693519047
2,33955747138043
1,03797322601538
0,393995225110537
-0,313133606691831
0,0153612718148083
0,334319255178859
-0,459411171763371
-0,140509165577489
0,00550671056401275
-0,323272139429302
0,0287534033256793
0,315430725438077
0,185946530306494
0,324718364827207
0,261095735135893
0,893826990599874
1,15461601882231
2,50413730606522
2,84734431626234
2,92579541786446
3,89734152899888
3,99966336639725
5,40208842062274
6,13558824651502
6,53536620995076
7,75041469409203
9,35802700412211
9,26915251736991
10,5277151548496
11,7334023655478
12,2388402410764
12,7373389255184
12,3111049503131
12,6793679366281
12,4956582165158
13,2924367296868
12,7891351108858
12,0769637304018
11,1376166094701
10,302623594405
9,31770787764564
8,54798648529227
7,78138339024316
7,41567768402507
6,19643282801022
5,1267114504003
4,40237026179274
3,98027505314497
1,34676951984201
1,18163367779434
0,584148560641762
0,489817620539382
-0,483281086930105
0,463827307803238
0,390004398438161
0
'''
s2 = '''0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
1,171875
1,8017578125
2,548828125
3,3544921875
4,658203125
5,3466796875
5,3466796875
6,650390625
7,3388671875
7,3388671875
7,8369140625
7,529296875
7,8369140625
7,8369140625
7,646484375
7,8369140625
6,591796875
5,712890625
5,0390625
4,1015625
3,9111328125
2,9150390625
2,3583984375
1,3623046875
0,3662109375
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0,9228515625
1,728515625
2,16796875
3,2958984375
4,8486328125
4,599609375
5,9033203125
6,9580078125
7,3388671875
7,7783203125
7,4560546875
7,646484375
7,4560546875
8,14453125
7,7783203125
7,08984375
6,4013671875
5,712890625
4,7900390625
4,04296875
3,2958984375
2,9150390625
1,728515625
0,732421875
0
0
0
0
0
0
0
0
0
0
'''


sun = [*map(float, sun.strip().replace(',', '.').split('\n'))]
s2 = [*map(float, s2.strip().replace(',', '.').split('\n'))]

x1, y1 = sun[20], s2[20]
x2, y2 = sun[77], s2[77]

# a = (y1 - y2) / (x1 - x2)
# b = y1 - a * x1

# a = 0.948112223169549
# b = -3.4673491194914865

# a = 0.8884815907514603
# b = -2.939533262956714

# a = 0.91183946117661
# b = -3.769696616882193

a = 0.945379
b = -3.345422

ap = [*(max(a * max(x, 0) ** 1.1278885 + b, 0) for x in sun)]

# plt.plot(range(len(sun)), sun)
# plt.plot(range(len(s2)), s2)
# plt.plot(range(len(sun)), ap)
# print(f'a = {a}, b = {b}')
# print(sum(abs(s2[i] - ap[i]) for i in range(len(ap))))

arr = sorted([*((sun[i], s2[i]) for i in range(len(sun)))], key=lambda x: x[0])

plt.plot([*(a[0] for a in arr)], [*(a[1] for a in arr)])
plt.grid(True)

plt.show()