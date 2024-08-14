"""
Author: Xander Peng
Date: 2024/8/1
Description: 
"""

''' Define the city clusters in 3 study areas '''
# China
JJJ = ["北京市", "天津市", "石家庄市", "唐山市", "邯郸市", "秦皇岛市", "承德市", "廊坊市", "沧州市", "衡水市", "张家口市"]
CSJ = ["上海市", "南京市", "杭州市", "苏州市", "宁波市", "无锡市", "常州市", "徐州市", "济南市", "合肥市", "温州市", "绍兴市", "金华市", "台州市",
       "嘉兴市", "湖州市", "舟山市", "衢州市", "丽水市"]
ZSJ = ["广州市", "深圳市", "珠海市", "佛山市", "东莞市", "中山市", "江门市", "肇庆市", "惠州市", "汕头市", "汕尾市", "湛江市", "茂名市", "阳江市",
       "潮州市", "揭阳市", "云浮市", "清远市"]

# USA; Here, we use the HASC_2 code to represent the cities
NM = ['US.CT.FA', 'US.CT.NH', 'US.CT.HA', 'US.CT.LI', 'US.CT.MI', 'US.CT.NL', 'US.CT.TO', 'US.CT.WI',
      'US.DE.NC', 'US.ME.AN', 'US.ME.CU', 'US.ME.KE', 'US.ME.LI', 'US.ME.OX', 'US.ME.SA', 'US.ME.YO',
      'US.MD.BC', 'US.MD.BA', 'US.MD.AA', 'US.MD.CA', 'US.MD.HA', 'US.MD.HO', 'US.MD.MO', 'US.MD.PG',
      'US.MA.BA', 'US.MA.BE', 'US.MA.BR', 'US.MA.DU', 'US.MA.ES', 'US.MA.FR', 'US.MA.HA', 'US.MA.HP',
      'US.MA.MI', 'US.MA.NA', 'US.MA.NO', 'US.MA.PL', 'US.MA.SU', 'US.MA.WO', 'US.NJ.SU', 'US.PA.MO',
      'US.NH.HI', 'US.NH.ME', 'US.NH.RO', 'US.NH.ST', 'US.NH.BE', 'US.NH.CA', 'US.NH.CH', 'US.NH.CO',
      'US.NH.GR', 'US.NH.SU', 'US.NJ.BE', 'US.NJ.BU', 'US.NJ.CA', 'US.NJ.ES', 'US.NJ.GL', 'US.NJ.HU',
      'US.NJ.HU', 'US.NJ.ME', 'US.NJ.MI', 'US.NJ.MO', 'US.NJ.OC', 'US.NJ.PA', 'US.NJ.SA', 'US.NJ.SO',
      'US.NY.BX', 'US.NY.KI', 'US.NY.NY', 'US.NY.QU', 'US.NY.RI', 'US.PA.BU', 'US.PA.CH', 'US.PA.DE',
      'US.PA.PH', 'US.RI.BR', 'US.RI.KE', 'US.RI.NE', 'US.RI.PR', 'US.RI.WA', 'US.VT.AD', 'US.VT.BE',
      'US.VT.CA', 'US.VT.CH', 'US.VT.ES', 'US.VT.FR', 'US.VT.GR', 'US.VT.LA', 'US.VT.OR', 'US.VT.RL',
      'US.VT.WA', 'US.VT.WI', 'US.VT.WN']

BAY_AREA = ['US.CA.AA', 'US.CA.CN', 'US.CA.MN', 'US.CA.NA', 'US.CA.SF', 'US.CA.SM', 'US.CA.SC', 'US.CA.SO', 'US.CA.SL']

# Europe
WE = ["Belgium", "France", "Germany", "Italy", "Luxembourg", "Netherlands", "United Kingdom"]
NE = ["Denmark", "Finland", "Iceland", "Norway", "Sweden"]
