"""
Author: Xander Peng
Date: 2024/8/1
Description: 
"""

''' Define the city clusters in 3 study areas '''
# China
JJJ = ["北京市", "天津市", "石家庄市", "唐山市", "邯郸市", "秦皇岛市", "承德市", "廊坊市", "沧州市", "衡水市", "张家口市"]
CSJ = ["上海", "南京", "杭州", "苏州", "宁波", "无锡", "常州", "徐州", "济南", "合肥", "温州", "绍兴", "金华", "台州",
       "嘉兴", "湖州", "舟山", "衢州", "丽水"]
ZSJ = ["广州", "深圳", "珠海", "佛山", "东莞", "中山", "江门", "肇庆", "惠州", "汕头", "汕尾", "湛江", "茂名", "阳江",
       "潮州", "揭阳", "云浮", "清远"]

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
