from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from ccg_web.settings import BASE_DIR
import os, os.path, sys, sqlite3

#Majority shit code blame Rama

DB_DIR = os.path.join(BASE_DIR, "CCG/gosb.db")

FONTS_DIR = os.path.join(BASE_DIR, "fonts")

CCG_PATH = os.path.join(BASE_DIR, "CCG/")

ASPECT_CHART={#  ASPECT_DAMAGE_CHART[attackaspectID][defenceaspectID]
	# 			1=Null 2=Flame 3=Water 4=Earth 5=Air 6=Holy 7=Fallen
	1:{"name":"Null",   1:1, 2:1,   3:1,   4:1,   5:1,   8:1,   6:0.5, 7:0.5,
	 "emoji":"<:null:640100942183923732>",   "prefix":"a1"},#None
	2:{"name":"Flame",  1:1, 2:0.5, 3:0,   4:1,   5:3,   8:1,   6:2,   7:1,
	   "emoji":"<:flame:638629899267211264>",  "prefix":"a2"},#},#Flame
	3:{"name":"Water",  1:1, 2:3,   3:0.5, 4:2,   5:1,   8:0,   6:1,   7:1,
	   "emoji":"<:water:638629932305743882>",  "prefix":"a3"},#},#Water
	4:{"name":"Earth",  1:1, 2:2,   3:1,   4:0.5, 5:0,   8:3,   6:1,   7:1,
	   "emoji":"<:earth:638629971358908426>",  "prefix":"a4"},#},#Earth
	5:{"name":"Air",    1:1, 2:0,   3:1,   4:3,   5:0.5, 8:1,   6:1,   7:2,
	   "emoji":"<:air:638630008046485504>",    "prefix":"a5"},#},#Air
	8:{"name":"Voltage",1:1, 2:1,   3:3,   4:0,   5:2,   8:0.5, 6:1,   7:1,
	   "emoji":"<:voltage:640051390068293644>","prefix":"a8"},#},#Voltage
	6:{"name":"Holy",   1:2, 2:0.5, 3:1,   4:1,   5:2,   8:1,   6:0.5, 7:3, 
	  "emoji":"<:holy:638630049481883658>",   "prefix":"a6"},#},#Holy
	7:{"name":"Fallen", 1:2, 2:2,   3:1,   4:1,   5:1,   8:1,   6:3,   7:0.5,
	 "emoji":"<:fallen:638630085196251146>", "prefix":"a7"},#},#Fallen
	
}

CARD_TYPES={
	1:{"name":"regular monster","emoji":"<:regular_monster:638759453805510656>","prefix":"mon_reg","ref":"RM"},
	2:{"name":"titan monster","emoji":"<:titan_monster:638759542322102332>","prefix":"mon_tit","ref":"TM"},
	3:{"name":"gear card","emoji":"<:gear_card:638759609422577674>","prefix":"gea","ref":"GR"},
	4:{"name":"magic card","emoji":"<:magic_card:638759677563240448>","prefix":"mag","ref":"MG"},
	5:{"name":"event card","emoji":"<:event_card:638759771184300052>","prefix":"eve","ref":"EV"},
}

CARD_SETS={
    1:{"name":"Base Set","num":246,"prefix":"bs","ref":"BS","boosters":2,
    "emoji":"<:base_set:639010294416277505>","path":CCG_PATH+"sets"+"/"+"baseset"},
    2:{"name":"Promo Set 1","num":116,"prefix":"pro","ref":"PRO","boosters":2,
    "emoji":"<:promo:639010377312763905>","path":CCG_PATH+"sets"+"/"+"promo"},
    3:{"name":"Sci-Fi Blockbuster","num":172,"prefix":"sfb","ref":"SFB","boosters":3,
    "emoji":"<:scifi_blockbuster:644417950174019609>","path":CCG_PATH+"sets"+"/"+"scifiblockbuster"},
    4:{"name":"Elder Scrolls Online","num":118,"prefix":"eso","ref":"ESO","boosters":2,
    "emoji":"<:elder_scrolls_online:647243415477682208>","path":CCG_PATH+"sets"+"/"+"eso"},
    5:{"name":"Exclusive","num":11,"prefix":"ex","ref":"EX","boosters":0,
    "emoji":"<:exclusive:648665412522999818>","path":CCG_PATH+"sets"+"/"+"exclusive"},
    6:{"name":"Marvel Vs DC","num":187,"prefix":"mvd","ref":"MVD","boosters":2,
    "emoji":"<:m_vs_dc:651599440716496938>","path":CCG_PATH+"sets"+"/"+"mvdc"},

}
SET_BOOSTER_PICS={
	1:{
		1:{"name":"Booster","num":2,1:{"emoji":"<:bstBS_1:641539164541550592>","url":""},
		2:{"emoji":"<:bstBS_2:641539187811680286>","url":""} },
		2:{"name":"Starter Deck","num":5,1:{"emoji":"<:deck_1:641539731074842624>","url":"","DeckID":1},
		2:{"emoji":"<:deck_2:641539765044379661>","url":"","DeckID":2},3:{"emoji":"<:deck_3:645119932245344264>","url":"","DeckID":3},4:{"emoji":"<:deck_4:646553703372816424>","url":"","DeckID":4},5:{"emoji":"<:deck_5:641539781456822292>","url":"","DeckID":5} },
		3:{"name":"Booster Box","num":2,1:{"emoji":"<:boxBS_1:641539211949768705>","url":""},
		2:{"emoji":"<:boxBS_2:641539231910592522>","url":""} },
	},
	2:{
		1:{"name":"Booster","num":2,1:{"emoji":"<:bstPRO_1:641959028075003915>","url":""},
		2:{"emoji":"<:bstPRO_2:641959117795229699>","url":""} },
		2:{"name":"Starter Deck","num":0,1:{"emoji":"<:deck_1:641539731074842624>","url":"","DeckID":1},
		2:{"emoji":"<:deck_2:641539765044379661>","url":"","DeckID":2},5:{"emoji":"<:deck_5:641539781456822292>","url":"","DeckID":5} },
		3:{"name":"Booster Box","num":0,1:{"emoji":"<:boxBS_1:641539211949768705>","url":""},
		2:{"emoji":"<:boxBS_2:641539231910592522>","url":""} },
	},
	3:{
		1:{"name":"Booster","num":3,1:{"emoji":"<:bstSFB_1:644103268129046528>","url":""},
		2:{"emoji":"<:bstSFB_2:644103399314423862>","url":""},3:{"emoji":"<:bstSFB_3:644103442104582154>","url":""} },
		2:{"name":"Starter Deck","num":0,1:{"emoji":"<:deck_1:641539731074842624>","url":"","DeckID":1},
		2:{"emoji":"<:deck_2:641539765044379661>","url":"","DeckID":2},3:{"emoji":"<:deck_5:641539781456822292>","url":"","DeckID":5},4:{"emoji":"<:deck_5:641539781456822292>","url":"","DeckID":5},5:{"emoji":"<:deck_5:641539781456822292>","url":"","DeckID":5} },
		3:{"name":"Booster Box","num":3,1:{"emoji":"<:boxSFB_1:644103735567581204>","url":""},
		2:{"emoji":"<:boxSFB_2:644103805566320655>","url":""},3:{"emoji":"<:boxSFB_3:644103849036218378>","url":""} },
	},
	4:{
		1:{"name":"Booster","num":2,1:{"emoji":"<:bstESO_1:647113064235401227>","url":""},
		2:{"emoji":"<:bstESO_2:647113087362531338>","url":""} },
		2:{"name":"Starter Deck","num":0,1:{"emoji":"<:deck_1:641539731074842624>","url":"","DeckID":1},
		2:{"emoji":"<:deck_2:641539765044379661>","url":"","DeckID":2},3:{"emoji":"<:deck_3:645119932245344264>","url":"","DeckID":3},4:{"emoji":"<:deck_4:646553703372816424>","url":"","DeckID":4},5:{"emoji":"<:deck_5:641539781456822292>","url":"","DeckID":5} },
		3:{"name":"Booster Box","num":2,1:{"emoji":"<:boxESO_1:648031068833710119>","url":""},
		2:{"emoji":"<:boxESO_2:648031132234940426>","url":""} },
	},
}
SET_BOOSTER_URLS={ #[SetID, BoosterTypeID,CoverID,NumCards]
	1:{#base set
		1:{#boosters
			1:{3:"https://i.postimg.cc/RC7QvJh4/booster3-1.png",5:"https://i.postimg.cc/g2JvyMD2/booster5-1.png",8:"https://i.postimg.cc/fTM7yWSX/booster8-1.png"},
			2:{3:"https://i.postimg.cc/SRfWd33J/booster3-2.png",5:"https://i.postimg.cc/c4TRnqfz/booster5-2.png",8:"https://i.postimg.cc/FHB0TjWg/booster8-2.png"},

		},
		2:{# decks
			1:"https://i.ibb.co/88Cyt0v/deck-1.png",
			2:"https://i.ibb.co/v4Jg4gV/deck-2.png",
			3:"https://i.postimg.cc/pXgNDZt3/deck-3.png",
			4:"https://i.postimg.cc/597KWx01/deck-4.png",
			5:"https://i.ibb.co/G2T3Brm/deck-5.png",
		},
		3:{# booster boxes
			1:"https://i.postimg.cc/d1dRkL9R/booster-X24-1.png",
			2:"https://i.postimg.cc/2yDQ4rHs/booster-X24-2.png",
		},	
	},
	2:{#Promo set 1
		1:{#boosters
			1:{3:"https://i.postimg.cc/2yG57znH/booster3-1.png",},
			2:{3:"https://i.postimg.cc/prRTj95h/booster3-2.png",},

		},

	},
	3:{#sci fi set
		1:{#boosters
			1:{3:"https://i.postimg.cc/vHmLYdxt/booster3-1.png",5:"https://i.postimg.cc/nrh7hvrh/booster5-1.png",8:"https://i.postimg.cc/7htzGfJM/booster8-1.png"},
			2:{3:"https://i.postimg.cc/T3LVbq9y/booster3-2.png",5:"https://i.postimg.cc/mr77XLKB/booster5-2.png",8:"https://i.postimg.cc/JnmZ9wWJ/booster8-2.png"},
			3:{3:"https://i.postimg.cc/sgkp4Q6T/booster3-3.png",5:"https://i.postimg.cc/9MpZ2xWk/booster5-3.png",8:"https://i.postimg.cc/Wp5gffYF/booster8-3.png"},

		},
		2:{# decks
			1:"https://i.ibb.co/88Cyt0v/deck-1.png",
			2:"https://i.ibb.co/v4Jg4gV/deck-2.png",
			5:"https://i.ibb.co/G2T3Brm/deck-5.png",
		},
		3:{# booster boxes
			1:"https://i.postimg.cc/DyDs74T7/booster-X24-1.png",
			2:"https://i.postimg.cc/jS7f2qxP/booster-X24-2.png",
			3:"https://i.postimg.cc/BvfKKWby/booster-X24-3.png",
		},	
	},
	4:{#ESO set
		1:{#boosters
			1:{3:"https://i.postimg.cc/J0kFF2MF/booster3-1.png",5:"https://i.postimg.cc/TPtB5btt/booster5-1.png",8:"https://i.postimg.cc/zBMM0rZW/booster8-1.png"},
			2:{3:"https://i.postimg.cc/wBqSB2Qt/booster3-2.png",5:"https://i.postimg.cc/GmJWrVGw/booster5-2.png",8:"https://i.postimg.cc/tT7w3gfp/booster8-2.png"},
		},
		2:{# decks
			1:"https://i.ibb.co/88Cyt0v/deck-1.png",
			2:"https://i.ibb.co/v4Jg4gV/deck-2.png",
			5:"https://i.ibb.co/G2T3Brm/deck-5.png",
		},
		3:{# booster boxes
			1:"https://i.postimg.cc/mkx2rN7H/booster-X24-1.png",
			2:"https://i.postimg.cc/SRWQY2Gt/booster-X24-2.png",
		},	
	},
}


CARD_RARITY={
	1:{"name":"Common","emoji":"<:common:639071280603070474>","filename":"CCG"+"/"+"icons"+"/"+"rarity_1.png"},
	2:{"name":"Uncommon","emoji":"<:uncommon:639071326375641099>","filename":"CCG"+"/"+"icons"+"/"+"rarity_2.png"},
	3:{"name":"Rare","emoji":"<:rare:639071369161867265>","filename":"CCG"+"/"+"icons"+"/"+"rarity_3.png"},
	4:{"name":"Legendary","emoji":"<:legendary:639071412094763008>","filename":"CCG"+"/"+"icons"+"/"+"rarity_4.png"},
	5:{"name":"Secret Rare","emoji":"<:secret_rare:641922492981837864>","filename":"CCG"+"/"+"icons"+"/"+"rarity_5.png"},
}

TEAMS={
    1:{"name":"Team Monarch","prefix":"t1"},
    2:{"name":"Team Sonic","prefix":"t2"},
    3:{"name":"Rebel Alliance","prefix":"t3"},
    4:{"name":"Justice League","prefix":"t4"},
    5:{"name":"Starfleet","prefix":"t5"},
    6:{"name":"Klingon Defence Force","prefix":"t6"},
    7:{"name":"Ministry of Silly Battles","prefix":"t7"},
    8:{"name":"Monty Python","prefix":"t8"},
    9:{"name":"Decepticon","prefix":"t9"},
    10:{"name":"Autobot","prefix":"t10"},
    11:{"name":"Galaxy One","prefix":"t11"},
    12:{"name":"Galactic Empire","prefix":"t12"},
    13:{"name":"Cthulhu Mythos","prefix":"t13"},
    14:{"name":"Legends of Tomorrow","prefix":"t14"},
    15:{"name":"Samurai Jack","prefix":"t15"},
    16:{"name":"Thundercats","prefix":"t16"},
    17:{"name":"Skynet","prefix":"t17"},
    18:{"name":"Yautja","prefix":"t18"},
    19:{"name":"Xenomorph","prefix":"t19"},
    20:{"name":"Arachnid","prefix":"t20"},
    21:{"name":"Ebonheart Pact","prefix":"t21"},
    22:{"name":"Daggerfall Covenant","prefix":"t22"},
    23:{"name":"Aldmeri Dominion","prefix":"t23"},
    24:{"name":"Daedra","prefix":"t24"},
    25:{"name":"Black Lantern","prefix":"t25"},
    26:{"name":"Green Lantern","prefix":"t26"},
    27:{"name":"Batman","prefix":"t27"},
    28:{"name":"Superman","prefix":"t28"},
    29:{"name":"Avengers","prefix":"t29"},
    30:{"name":"Spidey","prefix":"t30"},
    31:{"name":"Venom","prefix":"t31"},
    32:{"name":"Enforcers","prefix":"t32"},
    33:{"name":"Outlaws","prefix":"t33"},
}

theSTrap={1:""}
PERM_FX={
	1:{"name":"Hyperspeed Getaway",},
	2:{"name":"Elemental Attack Assist",},
	3:{"name":"Elemental Defence Assist",},
	4:{"name":"Elemental Health Assist",},
	5:{"name":"Elemental Speed Assist",},
	6:{"name":"Sacrificial Wish",},
	7:{"name":"Driven By Rage",},
	8:{"name":"Staunch Guardian",},
	9:{"name":"Rallying Cry",},
	10:{"name":"Sacrificial Sword",},
	11:{"name":"Sacrificial Sheild",},
	12:{"name":"Phoenix's Blessing",},
}

BOOSTER_TYPES={
	1:{"name":"Booster",},
	2:{"name":"Starter Deck",},
	3:{"name":"Booster Box",},

}
STARTER_DECKS={
	1:{"name":"Sonic Boom",},
	2:{"name":"Earth Trek",},
	3:{"name":"Basic Badasses",},
	4:{"name":"Robots & Heroes",},
	5:{"name":"Random Generated",},

}

class BasicCardInstance:

	def __init__(self,bc_id):		
		"""
		Assign all card variables within the class to ensure that the card is valid
		Screw python and its lack of private variables 
		"""
		self.BasicCardID=int(bc_id)
		print(self.BasicCardID)
		conn = sqlite3.connect(DB_DIR)
		c = conn.cursor()
		dbValues = []
		c.execute("SELECT * FROM tblBasicCards WHERE BasicCardID = ?;", (self.BasicCardID,))
		dbValues += c.fetchall()
		c.execute("""SELECT PFX.PermFXName, PFX.PermFXDescription
		 FROM tlkpPermFX PFX WHERE PFX.PermFXID IN
		  (SELECT BC.PermFXID FROM tblBasicCards BC WHERE BC.BasicCardID = ?);""", (self.BasicCardID,))
		dbValues += c.fetchall()
		c.execute("""SELECT TB.TitanBirthName, TB.TitanBirthDescription FROM
		 tlkpTitanBirth TB WHERE TB.TitanBirthID IN
		  (SELECT BC.TitanBirthID FROM tblBasicCards BC WHERE BC.BasicCardID = ?);""", (self.BasicCardID,))
		dbValues += c.fetchall()
		# TheCard = BasicCardInstance(dbValues[0][1],dbValues[0][2],dbValues[0][3],dbValues[0][4],dbValues[0][5],
		# 	dbValues[0][6],dbValues[0][7],dbValues[0][8],dbValues[0][9],dbValues[0][10],dbValues[0][11],dbValues[0][12],
		# 	dbValues[0][13],dbValues[0][14],dbValues[0][15],dbValues[0][16],dbValues[0][17],dbValues[0][18],dbValues[0][19],
		# 	dbValues[0][20],dbValues[0][21])
		self.BasicCardSetIndex=dbValues[0][1]
		self.BasicCardName=dbValues[0][2]
		self.BasicCardDescription=dbValues[0][3]
		self.CardTypeID=dbValues[0][4]
		self.SetID=dbValues[0][5]
		self.TypeID=dbValues[0][6]
		self.Type2ID=dbValues[0][7]
		self.RarityID=dbValues[0][8]
		self.AspectID=dbValues[0][9]
		self.CollectorNumber=dbValues[0][10]
		self.TeamID=dbValues[0][11]
		self.ATT=dbValues[0][12]
		self.DEF=dbValues[0][13]
		self.HP=dbValues[0][14]
		self.SPD=dbValues[0][15]
		self.TotalPoints=dbValues[0][16]
		self.TitanBirthID=dbValues[0][17]
		self.PermFXID=dbValues[0][18]
		self.SpellSpeed=dbValues[0][19]
		self.Value1=dbValues[0][20]
		self.Value2=dbValues[0][21]

		conn.close()

def createCardImage(card):
	Attack=card.ATT
	Defence = card.DEF
	Health= card.HP 
	Speed= card.SPD 
	PortraitName= "card_"+CARD_SETS[card.SetID]["prefix"]+str(card.CollectorNumber)
	PortraitPath=os.path.join(BASE_DIR, CARD_SETS[card.SetID]["path"]+"/"+"pics")
	PortraitFullPath=PortraitPath+"/"+PortraitName+".png"
	CardBackName="card_"+CARD_TYPES[card.CardTypeID]["prefix"]+"_"+ASPECT_CHART[card.AspectID]["prefix"]
	CardBackPath=os.path.join(BASE_DIR, CARD_SETS[card.SetID]["path"]+"/"+"cards")
	CardBackFullPath=CardBackPath+"/"+CardBackName+".png"
	SetSymbolFullPath=os.path.join(BASE_DIR, CARD_SETS[card.SetID]["path"]+"/"+"icons"+"/"+"set_icon.png")
	RaritySymbolFullPath=os.path.join(BASE_DIR, CARD_RARITY[card.RarityID]["filename"])
	

	BGimg = Image.open(CardBackFullPath)
	img = Image.open(PortraitFullPath)
	setImg=Image.open(SetSymbolFullPath)
	setImg=setImg.resize((30,30),Image.ANTIALIAS)
	rareImg=Image.open(RaritySymbolFullPath)
	rareImg=rareImg.resize((15,15),Image.ANTIALIAS)

	imgNew = BGimg.copy()
	#print()
	imgXY= imgNew.size
	imqQuad=Image.new(imgNew.mode,(400,600))
	#draw= ImageDraw.Draw(BGimg)
	imqQuad.paste(BGimg,(0,0))
	picXY=img.size
	if picXY==imgXY:
		imqQuad.paste(img,(0,0),img)
	else:
		imqQuad.paste(img,(25,33))
	imqQuad.paste(setImg,(9,565),setImg)
	imqQuad.paste(rareImg,(365,571),rareImg)

	if int(card.TeamID)!=0:
		TeamSymbolPath=os.path.join(BASE_DIR, CARD_SETS[card.SetID]["path"]+"/"+"teams")
		TeamSymbolImagePath=TeamSymbolPath+"/"+"team_"+TEAMS[card.TeamID]["prefix"]+"_"+ASPECT_CHART[card.AspectID]["prefix"]+".png"
		TeamImg=Image.open(TeamSymbolImagePath)
		imqQuad.paste(TeamImg,(310,7),TeamImg)

	draw = ImageDraw.Draw(imqQuad)
	font3 = ImageFont.truetype(os.path.join(FONTS_DIR, "segoeprb.ttf"), 20)
	draw.text((27, -2),str(card.BasicCardName),(0,0,0),font=font3)
	font2= ImageFont.truetype(os.path.join(FONTS_DIR, "segoeprb.ttf"), 11)
	colText=str(card.CollectorNumber)+"/"+str(CARD_SETS[card.SetID]["num"])
	draw.text((300, 570),str(colText),(0,0,0),font=font2)
	if card.CardTypeID==1 or card.CardTypeID==2:#if its a monster
		scoreText=str(card.TotalPoints)+" points"
		draw.text((50, 570),str(scoreText),(0,0,0),font=font2)
		font = ImageFont.truetype(os.path.join(FONTS_DIR, "segoeprb.ttf"), 22)
		txt = Image.new('RGBA', imqQuad.size, (255,255,255,0))
		d = ImageDraw.Draw(txt)
		d.text((113, 295),str(Attack),(0,0,0,64),font=font)
		d.text((279, 295),str(Defence),(0,0,0,64),font=font)
		d.text((113, 362),str(Speed),(0,0,0,64),font=font)
		d.text((279, 362),str(Health),(0,0,0,64),font=font)

		draw.text((111, 293),str(Attack),(0,0,0),font=font)
		draw.text((277, 293),str(Defence),(0,0,0),font=font)
		draw.text((111, 360),str(Speed),(0,0,0),font=font)
		draw.text((277, 360),str(Health),(0,0,0),font=font)
		
		
		if int(card.Type2ID)==0: #only one type
			TypePath=os.path.join(BASE_DIR,
			 "CCG"+"/"+"icons"+"/"+"types"+"/"+"type_"+str(card.TypeID)+"_"+ASPECT_CHART[card.AspectID]["prefix"]+".png")
			type1Img=Image.open(TypePath)
			imqQuad.paste(type1Img,(120,403),type1Img)
		else:# two types
			TypePath=os.path.join(BASE_DIR,
				 "CCG"+"/"+"icons"+"/"+"types"+"/"+"type_"+str(card.TypeID)+"_"+ASPECT_CHART[card.AspectID]["prefix"]+".png")
			type1Img=Image.open(TypePath)
			imqQuad.paste(type1Img,(20,403),type1Img)
			Type2Path=os.path.join(BASE_DIR, 
				"CCG"+"/"+"icons"+"/"+"types"+"/"+"type_"+str(card.Type2ID)+"_"+ASPECT_CHART[card.AspectID]["prefix"]+".png")
			type2Img=Image.open(Type2Path)
			imqQuad.paste(type2Img,(220,403),type2Img)
		
		if int(card.PermFXID)!=0:
			FXPath=os.path.join(BASE_DIR,
			 "CCG"+"/"+"icons"+"/"+"permfx"+"/"+"permfx_"+str(card.PermFXID)+".png")
			FXImg=Image.open(FXPath)
			imqQuad.paste(FXImg,(20,445),FXImg)
		if int(card.TitanBirthID)!=0:
			TBPath=os.path.join(BASE_DIR, 
				"CCG"+"/"+"icons"+"/"+"titanbirth"+"/"+"titanbirth_"+str(card.TitanBirthID)+".png")
			TBImg=Image.open(TBPath)
			imqQuad.paste(TBImg,(20,490),TBImg)
		imqQuad = Image.alpha_composite(imqQuad.convert("RGBA"), txt) 
		imqQuad=imqQuad.convert("RGB")
	elif card.CardTypeID==4 or card.CardTypeID==3 or card.CardTypeID==5: #a magic card
		#print("magic card")
		#print(card.BasicCardDescription)
		descriptionSplit=str(card.BasicCardDescription).split(" ")
		decriptionOutput=""
		linethreshold=33

		descriptionLine=""
		for word in descriptionSplit:
			if len(word)+len(descriptionLine)>linethreshold:
				descriptionLine+="\n"
				decriptionOutput+=descriptionLine
				descriptionLine=word+" "
			else:
				descriptionLine+=word+" "
		decriptionOutput+=descriptionLine 
		font4 = ImageFont.truetype(os.path.join(FONTS_DIR, "l_10646.ttf"), 19)
		draw.text((35, 304),str(decriptionOutput),(0,0,0),font=font4)

	return imqQuad



# async def GetCard(CardID):
# 	print("obtaining card")
# 	self.None
# 	conn = sqlite3.connect(DB_NAME)
# 	c = conn.cursor()
# 	c.execute("""
# 		SELECT TC.CardID AS CardID,TC.BasicCardID AS BasicCardID,
# 		(SELECT BC.BasicCardSetIndex FROM tblBasicCards BC WHERE BC.BasicCardID = TC.BasicCardID)
# 		 AS BasicCardSetIndex,(SELECT BC.BasicCardName FROM tblBasicCards BC WHERE  BC.BasicCardID = TC.BasicCardID)
# 		  AS BasicCardName, (SELECT BC.BasicCardDescription FROM tblBasicCards BC WHERE  BC.BasicCardID = TC.BasicCardID)
# 		   AS BasicCardDescription,(SELECT BC.CardTypeID FROM tblBasicCards BC WHERE  BC.BasicCardID = TC.BasicCardID)
# 		    AS CardTypeID,(SELECT BC.SetID FROM tblBasicCards BC WHERE  BC.BasicCardID = TC.BasicCardID)
# 		     AS SetID,(SELECT BC.TypeID FROM tblBasicCards BC WHERE  BC.BasicCardID = TC.BasicCardID)
# 		      AS TypeID,(SELECT BC.Type2ID FROM tblBasicCards BC WHERE  BC.BasicCardID = TC.BasicCardID)
# 		       AS Type2ID,(SELECT BC.RarityID FROM tblBasicCards BC WHERE  BC.BasicCardID = TC.BasicCardID)
# 		        AS RarityID,(SELECT BC.AspectID FROM tblBasicCards BC WHERE  BC.BasicCardID = TC.BasicCardID)
# 		         AS AspectID,(SELECT BC.CollectorNumber FROM tblBasicCards BC WHERE  BC.BasicCardID = TC.BasicCardID)
# 		          AS CollectorNumber,(SELECT BC.TeamID FROM tblBasicCards BC WHERE  BC.BasicCardID = TC.BasicCardID)
# 		           AS TeamID,(SELECT BC.Attack FROM tblBasicCards BC WHERE  BC.BasicCardID = TC.BasicCardID)
# 		            AS ATT, (SELECT BC.Defence FROM tblBasicCards BC WHERE  BC.BasicCardID = TC.BasicCardID)
# 		             AS DEF, (SELECT BC.Health FROM tblBasicCards BC WHERE  BC.BasicCardID = TC.BasicCardID)
# 		              AS HP, (SELECT BC.Speed FROM tblBasicCards BC WHERE  BC.BasicCardID = TC.BasicCardID)#
# 		               AS SPD,	(SELECT BC.TotalPoints FROM tblBasicCards BC WHERE  BC.BasicCardID = TC.BasicCardID)
# 		                AS TotalPoints, TC.AttackFudge AS AttackFudge,TC.DefenceFudge AS DefenceFudge,TC.HealthFudge
# 		                 AS HealthFudge,TC.SpeedFudge AS SpeedFudge,TC.OwnerID AS OwnerID,TC.CardRef AS CardRef,TC.ActualPoints AS ActualPoints,
# 		                 (SELECT BC.TitanBirthID FROM tblBasicCards BC WHERE BC.BasicCardID = TC.BasicCardID) AS TitanBirthID,
# 		                 (SELECT BC.PermFXID FROM tblBasicCards BC WHERE BC.BasicCardID = TC.BasicCardID) AS PermFXID,
# 		                 (SELECT BC.SpellSpeed FROM tblBasicCards BC WHERE BC.BasicCardID = TC.BasicCardID) AS SpellSpeed,
# 		                 (SELECT BC.Value1 FROM tblBasicCards BC WHERE BC.BasicCardID = TC.BasicCardID) AS Value1,
# 		                 (SELECT BC.Value2 FROM tblBasicCards BC WHERE BC.BasicCardID = TC.BasicCardID)
# 		                  AS Value2 FROM tblself. TC WHERE TC.CardID="+str(CardID)+";""")#only gets future dates and todays
# 	dbValues = c.fetchall()

# 	self.BasicCardInstance(dbValues[0][0],dbValues[0][1],dbValues[0][2],dbValues[0][3],dbValues[0][4],dbValues[0][5],dbValues[0][6],dbValues[0][7],dbValues[0][8],dbValues[0][9],dbValues[0][10],dbValues[0][11],dbValues[0][12],dbValues[0][13],dbValues[0][14],dbValues[0][15],dbValues[0][16],dbValues[0][17],dbValues[0][18],dbValues[0][19],dbValues[0][20],dbValues[0][21],dbValues[0][22],dbValues[0][23],dbValues[0][24],dbValues[0][25],dbValues[0][26],dbValues[0][27],dbValues[0][28],dbValues[0][29])
# 	conn.close()
# 	return TheCard

def getNumCards():
	conn = sqlite3.connect(DB_DIR)
	c = conn.cursor()
	return c.execute("SELECT MAX(BasicCardID) FROM tblBasicCards").fetchone()[0] + 1
	

def getAllCards():
	allCards = {}
	for i in range(1, getNumCards()):
		card = getBasicCard(i)
		allCards[str(i)] = card
	return allCards


def getBasicCard(ID):
	# print(ID)
	# conn = sqlite3.connect(DB_DIR)
	# c = conn.cursor()
	# dbValues = []
	# c.execute("SELECT * FROM tblBasicCards WHERE BasicCardID = ?;", (ID,))
	# dbValues += c.fetchall()
	# c.execute("""SELECT PFX.PermFXName, PFX.PermFXDescription
	#  FROM tlkpPermFX PFX WHERE PFX.PermFXID IN
	#   (SELECT BC.PermFXID FROM tblBasicCards BC WHERE BC.BasicCardID = ?);""", (ID,))
	# dbValues += c.fetchall()
	# c.execute("""SELECT TB.TitanBirthName, TB.TitanBirthDescription FROM
	#  tlkpTitanBirth TB WHERE TB.TitanBirthID IN
	#   (SELECT BC.TitanBirthID FROM tblBasicCards BC WHERE BC.BasicCardID = ?);""", (ID,))
	# dbValues += c.fetchall()
	# TheCard = BasicCardInstance(dbValues[0][0],dbValues[0][1],dbValues[0][2],dbValues[0][3],dbValues[0][4],dbValues[0][5],
	# 	dbValues[0][6],dbValues[0][7],dbValues[0][8],dbValues[0][9],dbValues[0][10],dbValues[0][11],dbValues[0][12],
	# 	dbValues[0][13],dbValues[0][14],dbValues[0][15],dbValues[0][16],dbValues[0][17],dbValues[0][18],dbValues[0][19],
	# 	dbValues[0][20],dbValues[0][21])
	# conn.close()
	# return TheCard

	#Compatibility function.
	#Should calss BasicCardInstance directly and avoid this function
	return BasicCardInstance(ID)

ALL_CARDS = getAllCards()

NUM_CARDS = getNumCards()
