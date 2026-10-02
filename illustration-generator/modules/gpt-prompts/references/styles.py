"""
视觉风格库 - GPT Image 2 风格参考

风格是 prompt 的 Style 部分，不是全部。
配合官方模板使用：类型 → 主体 → 场景 → 构图 → 风格 → 约束

GPT Image 2 已内置光影、构图、渲染能力，风格描述侧重"视觉调性"而非技术参数。
"""

STYLES = {
    "游戏截图": {
        "description": "游戏画面截图，像玩家在游戏中截的图",
        "styles": {
            "仙侠MMO游戏截图": {
                "style_instruction": "超高清仙侠MMO游戏截图风格，第三人称视角",
                "best_for": "古风仙侠场景、角色展示、城镇全景",
                "tips": "强调'游戏截图'而非'CG'，可要求带HUD（血条、技能栏、小地图）",
                "example": "Style: Ultra HD xianxia MMO game screenshot, third-person perspective. Game UI visible: health bars above characters, skill bar at bottom, minimap in corner, floating damage numbers."
            },
            "黑神话悟空风格": {
                "style_instruction": "黑神话悟空视觉风格，写实古风，大气磅礴",
                "best_for": "西游题材、古寺、山林、Boss战",
                "tips": "偏暗色调，强调'大气磅礴'和'写实'",
                "example": "Style: Black Myth Wukong visual style, photorealistic ancient Chinese aesthetic, dark atmospheric tone, grand scale."
            },
            "原神风格": {
                "style_instruction": "原神游戏截图风格，二次元渲染，明亮奇幻",
                "best_for": "奇幻风景、角色立绘、元素特效",
                "tips": "强调'明亮'和'奇幻'",
                "example": "Style: Genshin Impact game screenshot style, anime cel-shaded rendering, bright vibrant colors, fantasy atmosphere."
            },
            "赛博朋克游戏截图": {
                "style_instruction": "赛博朋克2077游戏截图风格，霓虹灯光，雨夜",
                "best_for": "未来城市、科技感场景",
                "tips": "雨夜+霓虹是标配，可加HUD",
                "example": "Style: Cyberpunk 2077 game screenshot, neon-lit rainy night city, game UI with health bar and minimap."
            },
        }
    },

    "像素游戏": {
        "description": "16-bit复古像素艺术风格——角色卡、游戏UI、CRT扫描线",
        "styles": {
            "16-bit动漫格斗角色卡": {
                "style_instruction": "16-bit复古像素艺术角色卡，模拟90年代格斗游戏角色选择界面。全画幅CRT扫描线纹理覆盖，锐利像素网格可见。竖版构图，金色细边框，角色半身居中。深色宇宙渐变背景（深靛蓝→紫色），点缀星光粒子。角色头顶大号像素风汉字名+英文全名。右侧竖排日文介绍文字+红色方形印章。左侧或底部属性条UI（ATTACK/SPEED/SPIRIT/LIFE等，红绿蓝橙彩色填充条）。底部显示LEVEL星级和队伍名。角落数字标记(1P)。整体高对比度、霓虹色调，角色技能特效以发光光环和粒子呈现",
                "best_for": "动漫/游戏角色档案卡、RPG角色面板、格斗游戏选人界面",
                "tips": "必加CRT扫描线纹理！属性条用不同颜色区分。角色招牌技能做成发光特效（灵丸/螺旋丸等）。左上角竖排标题，右下角艺术家签名。日文汉字+英文双语标注",
                "example": "Style: 16-bit pixel art character profile card, retro fighting game UI with CRT scanline overlay, vertical format. Dark cosmic gradient background with sparkles. Gold border frame. Character waist-up centered with signature move energy effect. Stat bars (ATTACK/SPEED/SPIRIT/LIFE) on the left. Vertical Japanese text sidebar on right. Level indicator at bottom. Pixel-perfect sharp edges, high contrast neon palette."
            },
        }
    },
    "影视截图": {
        "description": "电影/电视剧截图，有叙事感",
        "styles": {
            "电影级古风": {
                "style_instruction": "电影级古风画面，宽银幕构图，有叙事感",
                "best_for": "古装剧、历史题材、宫廷场景",
                "tips": "提具体朝代或故事背景比泛说'古代'好",
                "example": "Style: Cinematic ancient Chinese period drama frame, widescreen composition, rich warm color grading."
            },
            "电影级现代": {
                "style_instruction": "电影截图风格，有叙事感和情感张力",
                "best_for": "现代都市、人物特写、情感场景",
                "tips": "描述人物情绪和关系比描述技术参数重要",
                "example": "Style: Cinematic film still, moody atmospheric lighting, narrative framing."
            },
        }
    },
    "传统中国画": {
        "description": "中国传统绘画风格——工笔、写意、卷轴、壁画等",
        "styles": {
            "工笔神话卷轴": {
                "style_instruction": "中国传统工笔画风格，绢本/宣纸横卷，细线勾勒，矿物颜料设色，朱红印章，墨笔题款",
                "best_for": "山海经神兽对峙、仙佛斗法、神话叙事场景",
                "tips": "核心要素：①温暖米黄宣纸底色 ②工笔细线勾勒轮廓 ③矿物颜料设色（朱砂红、石青、石绿、赭石）④四角题款+朱红印章 ⑤如意云纹/山石松柏做背景 ⑥神兽毛发/羽毛要逐根精细描绘",
                "example": "Style: Traditional Chinese gongbi (fine brush) mythological painting on aged warm beige xuan paper, horizontal scroll format. Fine precise linework defining every feather and fur strand. Mineral pigment colors: cinnabar red seals, ink calligraphy, muted ochre and blue clouds. Ruyi-cloud patterns, shanshui mountains in background. Black ink calligraphy columns with cinnabar red seal stamps at corners."
            },
            "工笔花鸟": {
                "style_instruction": "传统工笔花鸟画，绢本设色，双钩填彩，精工细作",
                "best_for": "花鸟虫鱼、宫廷花卉、翎毛走兽",
                "tips": "强调'双钩填彩'技法，花瓣叶片要有层次晕染，背景留白或淡色渲染",
                "example": "Style: Traditional Chinese gongbi flower-and-bird painting on silk, double-outline filled color technique, meticulous detail, soft color gradients, pale background."
            },
            "工笔仕女": {
                "style_instruction": "传统工笔仕女图，唐宋宫廷画风，精细面部描绘，华丽衣饰",
                "best_for": "古代美人、宫廷场景、仕女图",
                "tips": "面部要'三白法'（额头/鼻梁/下巴留白），衣纹用铁线描，发丝要细密",
                "example": "Style: Traditional Chinese gongbi court lady painting, Tang-Song dynasty style, delicate facial features, elaborate hair ornaments, flowing silk robes with fine pattern detail."
            },
            "写意山水": {
                "style_instruction": "中国写意山水画，泼墨泼彩，留白，意境深远",
                "best_for": "山水意境、文人画、诗意表达",
                "tips": "强调'留白'和'意境'，笔触要概括不拘小节，墨分五色",
                "example": "Style: Traditional Chinese xieyi (freehand) landscape painting, expressive brushwork, ink wash gradients, generous negative space, misty mountains."
            },
            "敦煌壁画": {
                "style_instruction": "敦煌莫高窟壁画风格，矿物颜料，飞天造型，佛教题材，斑驳做旧",
                "best_for": "飞天、佛像、经变图、丝路题材",
                "tips": "色彩要浓烈但不艳俗（石青/石绿/朱砂/氧化变黑的铅白），画面要有岁月斑驳感，飞天衣带要飘举",
                "example": "Style: Dunhuang Mogao cave fresco painting style, mineral pigments (malachite green, azurite blue, cinnabar red), flying apsaras with flowing ribbons, aged patina and weathered texture, Buddhist iconography."
            },
            "怒相工笔": {
                "style_instruction": "朱砂红底工笔怒相画，古旧绢帛质感，深红背景满构图，怒目神明或凶兽填满画面，符箓飞舞，云纹中隐现鬼面败魂",
                "best_for": "怒相神明（怒目金刚/明王/斗战胜佛）、山海经凶兽特写、杀伐战阵、道教驱邪",
                "tips": "核心要素：①深朱砂红底色（不是米黄宣纸），模拟古旧血丝绢帛，有裂纹/斑驳 ②主体为单人/单兽大特写，填满画面，动态爆发感 ③面部要狰狞——獠牙、怒目（可三眼）、血溅 ④甲胄华丽，金饰+玉佩+飘带 ⑤背景云纹/烟雾/火焰中藏扭曲鬼脸和败魂 ⑥符箓（黄纸墨书）满天飞舞 ⑦色彩：朱砂红底 + 青绿/金/灰白主体 + 血红点缀 ⑧右下角可加画师朱文印章 ⑨用'like an authentic traditional Chinese painting, not digital art'约束",
                "example": "Style: Traditional Chinese gongbi (fine brush) wrathful deity painting on aged deep cinnabar-red silk/parchment background. Entire background is textured deep crimson with faint crackle and weathered patina simulating antique scroll material. Figure dominates center frame in dynamic explosive pose. Fine precise ink linework. Color palette: deep cinnabar red background, teal-blue-green and gilded gold armor, pale ashen skin, bright blood-red splatter accents. Swirling cloud and smoke forms in off-white, charcoal, and blood-red fill surrounding space, with tiny distorted screaming faces and writhing souls hidden within. Taoist paper talismans (fulu) flutter throughout. Fierce wrathful expression with bared fangs and glowing eyes. Must look like an authentic traditional Chinese painting, not digital art."
            },
            "水墨数字神明像": {
                "style_instruction": "水墨工笔×数字厚涂混合风格的神话角色竖版肖像，支持正/邪/傲三系。正系(神明/仙尊)：深靛蓝水墨晕染背景，金箔装饰，庄严神性。邪系(妖仙/魅魔)：深黑红金背景，暗红帷幕/灵体环绕，妖艳危险。傲系(桀骜少年神)：暴风云雾背景，红绸飞舞，叛逆挑衅，武器道具突出。共通要素：宣纸纹理全画幅覆盖，工笔细线勾勒面部+金饰，厚涂水彩表现衣袍，金色飘带流线+金箔碎点装饰，左上竖排标题+右下落款印章，参考画师玖肆风格",
                "best_for": "中国神话人物肖像（杨戬/王母等正系神明，妲己/九尾狐/红孩儿等邪系妖仙，哪吒/孙悟空/二郎神少年态等傲系桀骜神）、仙侠角色概念图、霸穹·封神演义同人、道教/佛教题材人物画",
                "tips": "【玖肆脸型比例（必须严格遵循，是和原画质量差距的关键）】①脸型：极度尖窄的V型脸（瓜子脸），最宽处在颧骨，下巴极尖极窄，下颌线急剧收窄 ②下巴：尖锐到近乎三角，脸部最窄点 ③眼睛：上挑狐狸眼（外眼角明显高于内眼角），半垂眼有神，眼宽≈1/4脸宽，大小适中不夸张 ④鼻子：极小极精致，窄低鼻梁，占脸1/6，低存在感 ⑤嘴：宽度只有两眼内角间距的2/3，唇小而饱满，上唇薄有Cupid's bow，下唇略厚 ⑥人中极短（约鼻长1/4）⑦三庭比约1:1:1.2（下巴略长显优雅）⑧颧骨低平不突出，平滑过渡到尖下巴 ⑨肤色：正系冷白瓷(#EAE3DC)，邪系暖白带粉红腮红。在prompt中写CRITICAL FACIAL PROPORTIONS段落强调这些比例【共通要素】①全画幅宣纸/绢本纹理叠加，笔触有水墨渗透感 ②主体偏右放置，面部在上1/3交叉点，左上留白放标题 ③面部用工笔细线——狭长凤眼、高挑眉，不写实要有神性 ④厚涂水彩表现衣袍，金色描边勾勒纹样(#D4AF37) ⑤金箔碎点(不等大小、不等透明度)散布全画 ⑥左上大号竖排中文标题(浅银灰)，下方小号英文/日文罗马音分两行 ⑦右下小号竖排画师签名+方形朱红印章 ⑧竖版传统挂轴比例(9:16)【正系变体·杨戬/哪吒等】①背景深靛蓝(#1A293A)水墨晕染，左上暗右下亮，模拟天界云雾 ②冷白肤(#EAE3DC)，薄唇，面部光洁神圣 ③服饰墨绿(#1E5044)+灰蓝(#435761)过渡+干笔肌理 ④金色飘带环绕头部肩部，半透明发光，代表天界灵气 ⑤半透明红(#A83244)/淡蓝(#7B9EB5)丝带点缀 ⑥光源右上偏暖，左侧面影融入雾气 ⑦氛围：regal, ethereal, solemn, divine, celestial【邪系变体·妲己/九尾狐等】①背景深黑(#0D0D0D)为主，血红帷幕(#8B0000)从右侧垂落，暗金纹饰 ②半透明白色灵体/狐灵环绕主体，红眼发光，融入水墨烟雾 ③主体后背可露半透明光环/曼荼罗，内含中式牌坊/宫殿剪影 ④暖白肤带微红腮红，半垂眼含媚态，唇色深红 ⑤服饰深血红+暗绿+黑，露出背部/肩部，可有符文刺青 ⑥金色发饰镶嵌红宝石，铃铛流苏垂坠 ⑦青铜灯笼/铜炉等古物点缀画面角落 ⑧氛围：opulent, ominous, seductive, ethereal, dangerous, divine【傲系变体·哪吒/孙悟空等桀骜少年·男性脸型（和女性V脸完全不同！）】①脸型：角形偏方，下颌宽度≈颧骨90%，不是瓜子脸！②下巴：方形，底部平坦宽大，不是尖三角 ③眼睛：锐利杏仁眼，上眼线直角上扬（不是柔和狐狸眼），眉骨突出压在眼眶上投下阴影 ④鼻子：高挺鼻梁，棱角分明，鼻翼宽于内眼角间距，鼻尖微方，突出显眼（不是极小精致鼻子）⑤眉毛：粗密几乎直平，只在尾部微上挑，压在眼睛上方（不是细弯弧眉）⑥三庭比≈1:1:1（更均衡）⑦颧骨宽阔明显 ⑧肤色暖白瓷带桃红腮红，骨骼感可见。在prompt中必须写MASCULINE FACIAL STRUCTURE段落强调，不能用女性V脸参数！⑨傲系背景：深靛蓝(#1A293A)+炭灰(#2C2C2C)暴风云雾，动感强烈，笔触比正系更粗犷狂放 ②姿态叛逆——下巴高抬，眼神挑衅傲慢，不闭目不垂眼，是上挑凤眼睁大 ③发型更自由：双丸子/飞蓬状高髻，红绸绑带从发间飞出，发丝狂乱 ④服饰半敞露胸/肩，轻薄透衣贴身，有金莲/火焰纹样，颜色偏亮白(#F0EDE8)+青蓝(#5B8FA8)+亮红 ⑤标志性武器道具必须露出（哪吒：乾坤圈/混天绫/风火轮暗光；孙悟空：金箍棒/如意金箍/紫金冠）⑥金饰比正系少但更粗犷——金环耳饰、胸甲项链，不要精细花丝 ⑦红绸/飘带数量多且动感极强，横贯画面，有速度线感 ⑧左上标题下方可加角色宣言/座右铭（竖排小字，如\"我命由我不由天\"）⑨氛围：defiant, rebellious, fierce, proud, untamed, kinetic, stormy",
                "example": "Style: Modern digital Chinese mythological portrait blending traditional ink wash and gongbi fine brush with digital watercolor impasto. Vertical scroll format (9:16). Full-canvas xuan paper texture overlay with visible ink bleed. Figure placed slightly right of center. [For righteous deities] Background: deep indigo (#1A293A) ink wash with celestial mist. Cool porcelain skin (#EAE3DC), malachite green (#1E5044) robes, gold foil aura, solemn divine mood. [For dark spirits/yokai] Background: near-black (#0D0D0D) with blood-red (#8B0000) drapery, semi-transparent white fox spirits with glowing red eyes swirling in ink smoke, warm pale skin with blush, deep crimson lips, ornate red-and-gold silk gown exposing bare shoulders with flame-pattern tattoo. Both variants: gongbi fine-line facial features, gold filigree hair ornaments, metallic gold (#D4AF37) linework, gold foil particle scatter, vertical title upper-left, artist seal lower-right. [For defiant young deities] Background: deep indigo (#1A293A) stormy clouds, charcoal grey (#2C2C2C) kinetic mist, dynamic aggressive brushwork. Chin raised defiantly, eyes wide-open and challenging. Free wild hairstyle with red ribbon streamers flying across the frame. Robes half-open revealing chest, gold lotus pectoral armor, lightweight translucent fabric. Signature weapon visible (universe ring, fire-tipped spear, or golden staff). Multiple red silk streamers cutting across the image with speed-line energy. Optional defiant quote below the title. Mood: defiant, rebellious, fierce, proud, kinetic."
            },
        }
    },
    "西方经典绘画": {
        "description": "西方经典绘画风格——印象派、后印象派、古典油画、浪漫主义等",
        "styles": {
            "印象派风景": {
                "style_instruction": "印象派户外写生油画风格，厚涂刮刀笔触（impasto），画布纹理可见，明亮自然光，光学混色",
                "best_for": "风景写生、田园牧场、河畔花田、雪山水景、户外人物",
                "tips": "核心要素：①厚涂笔触（impasto），能看到画布纹理 ②笔触方向要有意义（水平画水、垂直画倒影、曲线画树叶）③颜色在画布上混合而非预先调好 ④明亮户外自然光（plein air）⑤前景-中景-远景三层构图 ⑥前景可放人物背影做视觉锚点 ⑦用'visible canvas weave texture'和'individual visible brushstrokes'约束质感 ⑧用'Must look like an authentic hand-painted oil painting, not digital art'约束",
                "example": "Style: Impressionist plein air oil painting, thick visible impasto brushwork with visible canvas weave texture throughout. Bright natural daylight. Confident directional brushstrokes — horizontal for water, vertical for reflections, curved for foliage. Colors mixed on-canvas creating vibrant optical mixing. No blended smooth areas; every surface built from visible individual strokes. Must look like an authentic hand-painted oil painting with real texture, not digital art."
            },
            "后印象派": {
                "style_instruction": "后印象派油画风格，浓烈色彩，旋转笔触，主观情感表达，梵高/塞尚式",
                "best_for": "星空、麦田、向日葵、村庄夜景、情绪化风景",
                "tips": "笔触要有旋转和律动感，色彩要比实际更浓烈饱和，可以夸张变形表达情感，用' swirling rhythmic brushstrokes'描述笔触",
                "example": "Style: Post-impressionist oil painting in the manner of Van Gogh, thick swirling rhythmic brushstrokes, intensely saturated colors, emotionally charged landscape, every stroke alive with movement."
            },
            "古典油画肖像": {
                "style_instruction": "古典油画肖像风格，伦勃朗式明暗对比（chiaroscuro），深色背景，戏剧光源，细腻肌肤质感",
                "best_for": "人物肖像、历史人物、贵族、宗教人物",
                "tips": "强调单侧戏剧光源（chiaroscuro），背景要深暗不透明，肌肤要用半透明釉染法（glazing）质感，细节集中在面部和手部",
                "example": "Style: Classical oil painting portrait, Rembrandt-style chiaroscuro lighting, single dramatic light source from upper left, deep dark background, luminous skin with visible glazing layers, rich fabrics."
            },
            "浪漫主义风景": {
                "style_instruction": "浪漫主义风景油画，透纳式壮丽自然，暴风海浪/日落/雪崩，崇高感（sublime）",
                "best_for": "暴风雨、日落大海、雪山风暴、壮丽瀑布、灾难场景",
                "tips": "要表达自然的压倒性力量和人类的渺小，用极端天气和戏剧光影，天空占比要大，色彩要浓烈但不过于饱和",
                "example": "Style: Romantic landscape oil painting in the manner of J.M.W. Turner, sublime overwhelming nature, dramatic atmospheric light, storm clouds and churning seas, tiny human figures dwarfed by nature's power."
            },
        }
    },
    "故事书插画": {
        "description": "童话故事书、绘本、吉卜力式幻想插画风格——满构图、精致装饰、拟人角色、蒸汽朋克/奇幻元素",
        "styles": {
            "吉卜力蒸汽朋克童话": {
                "style_instruction": "吉卜力工作室风格蒸汽朋克童话插画，满构图，一点透视，宝石色调，拟人动物角色，大量装饰细节",
                "best_for": "奇幻城市全景、童话世界、蒸汽朋克街景、幻想绘本插图、魔法商店、游乐园/节日场景",
                "tips": "核心要素：①满构图——画面每个角落都塞满细节，不留空白 ②一点透视（运河/街道/走廊向远处延伸）③色调：宝石色（深蓝夜空、绿松石水、宝石红、鎏金、暖棕）④暖冷对比：上部冷色星空月光 vs 下部暖色灯笼火光 ⑤大量拟人动物角色（猫、兔、狗）穿衣服活动 ⑥蒸汽朋克元素：飞艇、齿轮、望远镜、古董钟 ⑦堆叠式建筑（店铺层叠、货架密集）⑧吊灯笼/彩灯/热气球点缀 ⑨远景奇幻城堡（白色尖塔+金色穹顶）⑩精致绘本插画质感，不是写实也不是纯动漫，介于两者之间",
                "example": "Style: Studio Ghibli-inspired steampunk fairy tale illustration, maximalist composition with zero empty space. One-point perspective down a turquoise canal through a sprawling fantasy city. Jewel-tone color palette: deep sapphire blue sky with full moon, ruby red velvet curtains, gilded gold trim, bright turquoise waterway, emerald green foliage, warm wood browns. Warm vs cool contrast — cold starlit sky above, hundreds of warm hanging lanterns below. Hundreds of tiny anthropomorphic animals (cats in hats and dresses, rabbits, dogs) shopping, boating, walking bridges. Stacked multi-level shop fronts with shelves crammed with antique clocks, telescopes, globes, maps, brass instruments. Steampunk airships, hot air balloons, flying whale in sky. Distant glowing white-and-gold fantasy castle with spires. Storybook illustration quality — detailed but whimsical, not photorealistic, not flat anime. Proscenium arch frame with red velvet curtains and gold tassels."
            },
        }
    },
    "插画/绘画": {
        "description": "各种插画和绘画风格",
        "styles": {
            "国风水墨": {
                "style_instruction": "中国水墨画风格，写意，留白，毛笔笔触",
                "best_for": "山水、花鸟、诗意场景",
                "tips": "强调'留白'和'写意'，不需要太多细节",
                "example": "Style: Traditional Chinese ink wash painting, expressive brushwork, generous negative space."
            },
            "日系赛璐璐": {
                "style_instruction": "日系动画截图风格，赛璐璐上色，干净线条",
                "best_for": "动漫角色、日常场景",
                "tips": "提'动画截图'比'插画'更像动画",
                "example": "Style: Japanese anime screenshot, cel-shaded coloring, clean linework."
            },
            "厚涂插画": {
                "style_instruction": "厚涂数字插画，笔触明显，色彩丰富",
                "best_for": "角色设计、概念图、封面",
                "example": "Style: Thick impasto digital illustration, visible brushstrokes, rich saturated colors."
            },
            "概念设计": {
                "style_instruction": "游戏/电影概念设计稿，干净背景",
                "best_for": "角色设计、道具设计",
                "tips": "可要求多角度展示",
                "example": "Style: Game concept art design sheet, white background, front/side/back views."
            },
            "手绘纹理角色设定稿": {
                "style_instruction": "动漫/游戏角色设定参考稿（character design reference sheet），铅笔速写线条+薄涂马克笔上色，粗糙手绘笔触，纹理纸背景，日式动画官方设定集草稿风格",
                "best_for": "动漫/游戏角色设定稿、同人角色参考图、概念设计展示、角色档案卡、二次元角色百科式展示",
                "tips": "⚠️已验证可用（9.5/10）关键经验：①【媒介描述】用'pencil sketch + thin marker coloring'而非'watercolor/colored pencil'——前者GPT-2能精准还原马克笔薄涂质感，后者会导致过重的数码渲染感②【线条】'rough pencil linework with visible sketch strokes and hatching shadows'比详细分级描述更有效，模型自会生成粗细变化③【上色】'colors stay loosely within line boundaries'一句话搞定半透明不溢出的效果，不需要长篇描述④【prompt简洁直接】不要写几十条约束规则（禁矢量线/禁3D/禁数码渲染等），GPT-2会被过度约束搞乱。简洁描述目标媒介+布局即可⑤【布局】直接列清单更有效：'expression sketches, isolated helmet/sword/boot detail, eye close-up, boot design, back view of costume, color palette section, artist signature'，模型会自动排布⑥【特效】'light colored pencil strokes'描述发光效果，比'glow/bloom'更自然⑦【标注】直接说'handwritten Japanese annotations'即可，不需要描述字号分级/排版规则",
                "example": "Style: Anime official character design sheet, pencil sketch on textured cream drawing paper. Rough pencil linework with visible sketch strokes and hatching shadows. Thin marker coloring with slight hand-drawn feel, colors stay loosely within line boundaries. Textured paper background with natural grain. Handwritten pencil-style Japanese annotations.\n\nLayout: Full-body dynamic combat pose in the center. Surrounding areas contain — expression sketches (calm, battle cry, surprised), isolated armor/weapon detail drawings, eye close-up, boot design, back view of costume. Bottom-left: 5-6 color swatches labeled in Japanese. Bottom-right: artist signature. All annotations in handwritten Japanese. Clean white space between sections."
            },
            "精致美宣立绘": {
                "style_instruction": "精致美宣立绘（游戏美宣/角色立绘），半写实数字插画，无线条纯色块+柔和渐变渲染，1:7.5头身比例，微动漫化五官但不过度夸张，柔和漫反射自然光，浅景深虚化背景",
                "best_for": "游戏/小说角色立绘、OC角色展示、角色肖像画、角色宣传海报、IP角色官方设定图",
                "tips": "⚠️已验证可用关键经验：①【渲染核心】'semi-realistic digital painting, no black outlines, smooth gradient blending'是关键，GPT-2默认会画线条，必须明确no outlines②【比例】'idealized 7.5-head proportions, moderately larger eyes than realistic but not oversized anime'③【皮肤质感】'soft luminous skin with subtle subsurface scattering'一句搞定通透肌肤感④【光影】'high-key soft diffused natural daylight, low contrast, no harsh shadows'⑤【背景】'shallow depth of field, blurred background that matches character theme, minimal environmental detail'⑥【材质】不同材质用不同描述：皮肤=subsurface scattering，金属=soft specular highlights，宝石=refractive highlights，布料=matte diffuse⑦【签名】'faint handwritten character name in top-left corner, faint PLAYFORGE signature in bottom-right'⑧【色彩策略】'tightly curated limited palette: neutral base + one signature accent color + gold accessory accents, slightly desaturated, no neon tones'",
                "example": "Style: PLAYFORGE style polished character illustration. Semi-realistic digital painting, no black outlines, all form edges defined purely by light and shadow. Smooth gradient blending with soft round brushes for skin and fabric, precise brushes for hard surfaces. Idealized 7.5-head proportions with moderately large expressive eyes, soft delicate facial features. Soft luminous skin rendered with subtle subsurface scattering. High-key soft diffused natural daylight, low contrast, gentle warm ambient fill, no harsh shadows. Shallow depth of field — blurred theme-matching background with minimal environmental detail. Tight limited color palette: neutral base tones, one signature accent color, gold accessory accents. Material-accurate rendering: subsurface scattering on skin, matte diffuse on fabric, soft speculars on metal, refractive highlights on gemstones. Faint handwritten character name (Chinese + English) in top-left corner, faint PLAYFORGE signature in bottom-right. Vertical portrait composition, medium-full body framing, soft friendly character expression."
            },
            "冰蓝清冷速写Sheet": {
                "style_instruction": "角色多姿态速写Sheet（character pose/expression sheet），纯白背景大量留白，浅灰黑细流畅手绘轮廓线+淡色辅助线，低饱和冷调薄涂水彩质感，4头身萌系Q版比例，三行等距排版，同一角色多个不同动态，飘逸灵动风格",
                "best_for": "ACG角色姿态设定Sheet、同人角色动作参考图、Q版角色多姿态展示、角色表情/动作集",
                "tips": "⚠️已验证（来源：voxcat神里绫华pose sheet）关键经验：①【线条】浅灰黑色（非纯黑）细线，外轮廓稍粗0.3-1px，内部更纤细，流畅松弛有手绘抖动感，不用粗重描边②【色彩】低饱和冷调，奶白+灰调冰蓝+浅绀蓝+浅金色点缀，饱和度≤30%，明度≥70%，薄涂水彩质感无厚重阴影③【背景】纯白留白，脚下加极细淡灰/淡蓝曲线做动态衔接线，角色间距充足互不重叠④【角色比例】4头身萌系二次元，头部稍大，四肢纤细，面部简化软萌⑤【排版】3行等距均匀排列，每行4-5个角色，像官方设定集速写稿⑥【装饰】极简极小（≤角色1/10），细线+淡色平涂，匹配主题的小元素（雪花/花瓣/音符/火焰等）⑦【氛围】清冷雅致/飘逸灵动/简约干净，根据主题可换⑧【色彩可替换】冰蓝→暖粉/竹绿/朱砂红/橙黄等，装饰元素同步替换⑨prompt简洁直接，不要堆禁令，描述目标媒介即可",
                "example": "Style: Anime character pose and expression sheet on pure white background with generous white space. Light grey-black thin fluid hand-drawn outlines (0.3-1px), slightly thicker on outer contours, delicate inner detail lines, loose natural sketchy feel. Low-saturation cool-tone thin watercolor wash coloring — pale cream white, muted ice blue, soft navy blue, pale gold accents. Saturation ≤30%, brightness ≥70%, no heavy shadows, thin translucent wash texture. 4-head-tall cute chibi proportions, large heads, slender limbs, simplified soft facial features. 3 rows of evenly spaced character poses (4-5 per row), each showing a different dynamic pose or expression, clean spacing with no overlap. Faint thin pale-blue curve lines at feet connecting poses. Tiny minimal decorative elements (snowflakes, petals, small themed motifs) drawn in thin lines with pale flat color fills, very small scale. Overall atmosphere: elegant, airy, graceful, clean and minimal. Looks like an official anime studio character design sketch sheet."
            },
            "美漫狂暴封面": {
                "style_instruction": "美式漫画封面风格（90s western superhero comic cover），粗黑描边+硬朗赛璐璐分区上色，极致饱和高对比，扁平纯色背景，夸张狂暴表情，漫画气泡/音效字/标题框等漫画排版元素",
                "best_for": "角色狂暴化二创、反差萌恶搞、美漫风角色封面、Meme式角色图、游戏角色恶搞周边图",
                "tips": "⚠️经验：①【线稿核心】'thick heavy variable-weight bold black ink outlines'——外轮廓最粗，内部线条稍细但仍粗硬，绝对不能有柔和线条②【上色】'hard-edged cel shading, flat colors, 2-3 shadow layers max, minimal soft gradients only for tiny specular highlights'——绝大部分区域是纯色块+硬边阴影，只有宝石/口水等微小高光有渐变③【背景】'100% flat single bold saturated solid color background, zero texture, zero gradients'——一整块纯色，不画任何背景细节④【表情】'extreme overexaggerated feral maniacal expression, wide crazed eyes, massively open mouth full of sharp teeth, drool/saliva detail'——必须狂暴化，不要温和表情⑤【构图】'chest-up close-up framing, one raised hand gesture, dynamic foreshortening toward viewer'——半身特写+手部动作⑥【漫画元素】必须包含：jagged spiky speech bubble with bold stylized text, small cartoon graphic emotion flourishes (stars/bursts), artist signature with tiny crown motif⑦【色彩】'highly saturated bright palette, high contrast between shadows and base colors'——拒绝柔和/低饱和",
                "example": "Style: 90s western superhero comic cover art style fused with anime character design. Thick heavy variable-weight bold black ink outlines — extra thick on character outer perimeter, slightly thinner for internal details, all lines crisp and sharp with zero softness. Hard-edged cel shading with flat color fills, maximum 2-3 shade layers per color (base + dark shadow block + small sharp highlight), highly saturated bright color palette with extreme contrast. 100% flat single bold solid color background with zero texture or detail. Extreme overexaggerated feral maniacal expression: wide crazed eyes, massively stretched open mouth full of rows of sharp pointed teeth, long tongue out, drool/saliva dripping detail. Chest-up close-up framing, one hand raised in dynamic claw gesture toward viewer. Jagged spiky western comic speech bubble with bold mixed-font text — standard sans-serif for secondary text, oversized scratchy bold colored text for key emphasis word. Small cartoon graphic flourishes (star bursts, impact marks) for emotional emphasis. Stylized artist signature at bottom corner."
            },
        }
    },
    "摄影": {
        "description": "真实摄影风格",
        "styles": {
            "人像写真": {
                "style_instruction": "专业人像摄影，浅景深，突出人物",
                "best_for": "个人写真、时尚摄影",
                "tips": "描述服装和情绪，不需要写镜头参数",
                "example": "Style: Professional portrait photography, shallow depth of field, soft natural lighting."
            },
            "街拍纪实": {
                "style_instruction": "街头纪实摄影，真实感，抓拍",
                "best_for": "城市生活、人文场景",
                "tips": "强调'生活气息'和'正在发生的事'",
                "example": "Style: Street documentary photography, candid moment, urban atmosphere."
            },
            "商业产品": {
                "style_instruction": "商业产品摄影，干净背景，突出细节",
                "best_for": "商品展示、食物摄影",
                "tips": "越简洁越好",
                "example": "Style: Commercial product photography, clean dark background, precise studio lighting."
            },
        }
    },
    "设计/海报": {
        "description": "平面设计和海报",
        "styles": {
            "电影海报": {
                "style_instruction": "好莱坞电影海报风格，戏剧性构图，大片感",
                "best_for": "宣传海报、活动海报",
                "example": "Style: Hollywood movie poster, dramatic composition, epic scale."
            },
            "社交媒体配图": {
                "style_instruction": "社交媒体高质量配图，竖版，视觉冲击力",
                "best_for": "小红书、朋友圈、Instagram",
                "tips": "竖版(9:16)，第一眼要有吸引力",
                "example": "Style: High-quality social media vertical image, eye-catching composition, lifestyle aesthetic."
            },
            "国潮概念海报": {
                "style_instruction": "国潮AIGC概念海报，杂志编辑式排版，暗夜底色+暖金光源，高精度CG级古风人物，大量中文排版文字作为画面构成元素，牡丹/祥云/宫殿等传统元素",
                "best_for": "历史人物概念海报、古风品牌视觉、国潮杂志封面、文化IP概念设计",
                "tips": "核心要素：①暗夜/深色背景 ②主体人物CG级渲染（高精度写实+幻想化古风）③暖金方向光打亮人物服饰，营造奢华梦幻感 ④大面积中文排版——标题用大号书法/宋体竖排，副标题/诗句用小号横排或竖排分区块 ⑤传统元素（牡丹花瓣飘落/宫殿建筑/月亮/祥云）⑥底部品牌/创作者AIGC标签 ⑦文字即设计——排版本身就是画面构成，不要把文字当标签贴，要融入构图 ⑧竖版9:16 ⑨标题文字要在prompt中明确写出内容和位置",
                "example": "Style: Chinese Guochao AIGC concept poster, magazine editorial layout. Dark night background with warm golden directional lighting. Central figure in high-fidelity CG-rendered fantasy traditional Chinese costume, mid-dance dynamic pose. Large traditional Chinese title text in calligraphic font at top left as dominant graphic element. Scattered vertical and horizontal text columns in smaller elegant serif font across the image — poetry, descriptions, labels — acting as design elements integrated into composition. Floating peony petals throughout. Traditional palace architecture in background. Luxurious romantic dreamlike atmosphere. Vertical 9:16 format."
            },
            "央视古装剧海报": {
                "style_instruction": "2000年代中期央视古装电视剧海报风格，柔焦暖紫色调，浅景深聚焦主角，书法金字竖排标题，传统道具摆拍（笔墨纸砚/瓷器），浪漫叙事氛围，传统繁体字演职员表",
                "best_for": "古装言情剧概念海报、古装人物宣传、传统爱情故事视觉化",
                "tips": "核心要素：①柔焦浅景深——主体清晰、背景模糊（瓷器/花枝/窗帘/灯笼）②暖紫+棕金+米白配色③主角穿汉fu/古装，手持传统道具（毛笔/折扇/茶杯）④前景桌案布景（笔墨纸砚/青瓷花瓶/梅枝/暗红桌布）⑤大号金色书法竖排标题（带纹理质感）⑥竖排传统繁体字演职员表（導演/編劇/領銜主演）⑦底部红色印章（'古裝巨獻'等）⑧'CCTV-8 黄金强檔'等播出台标⑨浪漫柔光，暖黄灯笼光⑩竖版9:16海报构图",
                "example": "Style: 2004 CCTV period romance TV drama promotional poster. Soft warm purple-brown-gold color palette with shallow depth of field. Central figure in traditional Hanfu, posed over a dark plum-purple cloth-covered table with calligraphy brush, rice paper, inkstone, and brush pot. Blurred background with blue-and-white porcelain vase holding plum blossoms, heavy burgundy curtains, warm lantern light, wooden lattice windows. Large textured gold vertical brush calligraphy title at upper left. Vertical traditional Chinese credits (導演/編劇/領銜主演) in elegant serif font. Red seal stamp at bottom. Romantic, nostalgic, atmospheric mood. Vertical poster format."
            },
            "九十年代胶片古装海报": {
                "style_instruction": "1990年代中国古装电影/电视剧海报风格，做旧泛黄纸张质感，褪色棕褐色调，毛边破损边缘，胶片颗粒感，简朴竖排排版，传统庭院背景",
                "best_for": "经典文学改编概念海报、年代感古装宣传、复古怀旧影视视觉",
                "tips": "核心要素：①做旧泛黄纸张底色，有年龄斑点（age spots）和纤维纹理 ②右上角毛边撕裂破损 ③褪色棕褐色调（不是黑白也不是全彩，是褪色的暖棕）④胶片颗粒感 ⑤主角古装特写，柔和中焦 ⑥背景虚化的传统庭院（竹林/粉墙/石阶/木柱）⑦竖排书法标题（左上，大号黑墨）⑧右上竖排片种标注（'二十集故事片'/'彩色宽银幕'）⑨竖排诗句/题词（红棕色）⑩底部竖排演职员表+制片厂名（红棕色小字）⑪右下角大号年份数字（如'1993'）⑫竖版海报构图",
                "example": "Style: 1990s Chinese period drama film poster, printed on aged faded sepia paper with small age spots and fiber texture visible. Ragged torn edge at top right corner. Desaturated warm brownish color palette with faded purples and muted earth tones. Film grain texture throughout. Soft-focus shallow depth of field — traditional courtyard alley background with bamboo stalks, whitewashed walls, grey stone steps, dark wooden pillars. Subject in traditional layered Hanfu (cream inner robe, lavender outer robe with dark purple floral trim), hair in traditional updo with enamel hairpins and jade drop earrings. Large bold black vertical brush calligraphy title at upper left. Small reddish-brown rectangular seal. Vertical credits in small reddish-brown serif font at bottom left (编剧/导演/摄影/作曲). Large reddish-brown year number at bottom right. Vertical poster format."
            },
            "动漫杂志收藏封面": {
                "style_instruction": "动漫角色时尚杂志收藏封面，Vogue×二次元联名刊风格。中央角色时尚pose+华丽坐具/布景，两侧边栏塞满编辑文字和收藏品小物（邮票/chibi/拍立得/手办/票根/火漆印），顶部超大半透明标题叠在角色身后，底部footer标语。整体像剪贴簿分层拼贴，每个小物都有1-2°倾斜和纸质纹理阴影",
                "best_for": "游戏/动漫角色收藏封面、角色生日贺图、限定刊概念设计、IP角色时尚大片",
                "tips": "核心要素：①布局三栏——左右各20%边栏+中间60%角色区 ②顶部header三段式（左logo/中品牌名/右标语）③大标题占页面上30%，半透明浅色叠在角色身后，上面叠加艺术家签名花体字 ④左栏=编辑文字为主（卷号/专题名/4-6行栏目标题+副标题）+底部拍立得+收藏卡+chibi贴纸 ⑤右栏=收藏品图形为主（3枚齿孔邮票chibi+牛皮纸便签卡+2张重叠活动票根+火漆印+缎带蝴蝶结）+角色名/台词/手写签名 ⑥角色居中坐华丽欧式椅子/布景，穿高定礼服，pose优雅慵懒 ⑦角色面部和躯干永远在最上层，文字/小物只搭到裙摆/椅子边缘 ⑧底部居中：缩放手办（黑底座+金色名牌）叠在角色脚前 ⑨最底footer：花体标语+小字期号 ⑩配色统一冰蓝/粉/银为主色系（按角色可换），牛皮纸暖棕做收藏品质感 ⑪所有小物有纸质纹理+5-10%透明度投影+1-2°微倾斜=手贴感 ⑫竖版9:16 ⑬必须传参考图控制排版精度",
                "example": "Style: Anime character fashion magazine collectible cover, Vogue × anime crossover special issue layout. Scrapbook layered collage aesthetic with subtle paper texture and soft drop shadows on every element.\n\nLAYOUT (vertical 9:16):\n- Top 7%: Header bar split in 3 — left: brand logo, center: faction/series name in caps, right: diamond icon + tagline\n- Top 7-32%: Giant semi-transparent title text (30% opacity, muted color) spanning full width BEHIND the character's head. Thin cursive artist signature overlaid at mid-height of the title.\n- Left 20% margin (height 30-88%): Editorial text column — volume/issue, 4-6 feature headlines with subtitles, circular ink seal stamp. Bottom: off-white polaroid headshot with handwritten signature, kraft paper collector card with barcode, die-cut chibi sticker.\n- Center 60% (height 20-94%): Character seated on ornate rococo chair in elegant high-fashion gown, soft smile, relaxed confident pose. Well-lit, detailed fabric/jewelry rendering. At bottom center: 1/7 scale pre-painted figure of same character on black base with gold nameplate, overlapping character's feet.\n- Right 20% margin (height 20-97%): Character name + Chinese name, character quote in quotation marks, handwritten cursive signature with tiny doodle. 3 perforated-edge postage stamps with chibi illustrations. 2 kraft paper note cards. 2 overlapping event tickets with postmark. Gold wax seal. Small ribbon bow at bottom.\n- Bottom 94-100%: Centered cursive tagline, small print issue number below.\n\nCOLOR: Icy periwinkle blue, off-white/cream, pale silver as primary. Deep royal blue for text. Warm kraft beige for ephemera. Metallic gold accents.\nTYPOGRAPHY: Large title = old-style serif uppercase semi-transparent. Sidebar headlines = bold serif uppercase dark. Subtext = thin sans-serif light gray. Signatures = loose handwritten cursive.\nCOMPOSITION: Character face/torso always topmost layer. Margins filled 90% capacity. All small items rotated 1-2° with paper texture and drop shadows for physical scrapbook feel."
            },
            "品牌联动商业海报": {
                "style_instruction": "动漫角色×真实品牌联动限定商业宣传海报。动漫人物立绘+现实场景+专业版式分区+品牌元素+产品突出。整体像官方联名活动的线下门店海报或社交媒体宣传图",
                "best_for": "动漫IP×饮品/食品/零售品牌联动海报、限定产品宣传、角色×品牌联名视觉、季节限定campaign",
                "tips": "核心要素：①构图：右侧2/3人物主视觉区+左侧1/3留白信息排版区，不要做成全出血拼贴 ②人物：高完成度动漫美少女立绘，线条干净五官精致，必须保留角色核心辨识特征（如毛利兰尖角刘海、红色发箍）③服装：不用原作校服，改为品牌联名单品造型（青春/清新/轻奢，配色跟随品牌色系）④场景：真实品牌门店外景/内景，摄影质感，动漫人物自然融入现实场景 ⑤饮品/产品：人物手持互动，产品外观精致诱人，品牌标识清晰可见 ⑥版式分层——左上：品牌logo / 中部：产品名（大号设计字体+英文副标题）/ 中下：宣传语（温柔青春） / 底部：价格+配料/成分小图标 ⑦色调跟随品牌主色（如星巴克=深绿+奶白+金色）⑧文字在prompt中明确写出内容和位置 ⑨约束：no school uniform, no clutter, no watermark, no distorted text ⑩推荐模型：gpt-image-2，分辨率2k起步",
                "example": "Style: Premium modern vertical commercial collaboration poster between an anime character and a real-world brand. The poster has a clear split layout: the right two-thirds features a high-quality anime illustration of the character naturally composited into a realistic brand store scene (photography-quality background), the left one-third is a clean gradient space for typography and branding. Fresh, modern, polished aesthetic matching the brand's visual identity. The anime character is drawn in premium commercial illustration style — clean linework, detailed shading, elegant proportions. The character holds the collaboration product prominently, interacting with it naturally. Brand logos, product name, price, and ingredients are clearly laid out on the left typography area with proper visual hierarchy. Overall looks like an official brand campaign poster suitable for both social media and in-store display."
            },
            "科技信息图海报": {
                "style_instruction": "现代科技产品发布风格的信息图海报，白底，圆角卡片布局，主色亮红(#E74C3C)，辅助灰/蓝/金，数据可视化元素，扁平化设计，6个结构化分区块（数据行/核心特点/优劣势VS/流程/实用信息/引用评价），竖版9:16手机屏优化",
                "best_for": "产品功能解析、数据展示、旅行攻略、知识科普、竞品对比、行业报告可视化、任何主题的全解析海报",
                "tips": "核心要素：①纯白背景，干净整洁 ②竖版9:16（手机传播更优）③顶部：大号粗体标题(黑) + 副标题(灰) + 红点日期标记，右上放主题相关红色线稿插图（风景/人物/建筑）+ 署名 ④数据行：5个圆角白卡片，大号粗体数字 + 小号中文标签 + 红色下划线 ⑤6个Section结构：核心特点(4卡片)→优劣势VS(双栏)→流程/阶段(4卡片+箭头)→实用信息(5卡片)→引用评价(2卡片)→底部CTA ⑥所有文字在prompt中明确写出具体内容 ⑦右上角主题线稿是灵魂，不要用通用图标 ⑧推荐先用纯prompt生成v1，再用edit模式微调 ⑨完整模板见 references/templates/infographic_poster/base.md",
                "example": "Style: Modern tech product launch infographic poster, clean white background, vertical 9:16 portrait format. Structured grid layout with rounded white cards, subtle shadows. Primary bright red (#E74C3C) accent, supporting grey (#888), blue (#3498DB), gold (#D4A017). Top: large bold black title + grey subtitle + red dot date, top-right thematic red line-art illustration + signature. Stats row: 5 rounded cards with bold numbers, grey labels, red underlines. Section 01: 4 cards with colored numbered circles (01-04). Section 02: VS split layout (red left vs grey right). Section 03: 4 cards connected by red arrows. Section 04: 5 cards with red icons. Section 05: 2 quote cards with red quotation marks. Bottom: slogan + red CTA button + logo. All text explicitly specified. Flat design, professional data-driven aesthetic."
            },
            "历史传记史诗海报": {
                "style_instruction": "好莱坞历史传记电影史诗海报风格，多层复合构图（幽灵半身像+全身高糊/远景+建筑景观背景），奢华金+深皇家蓝+象牙白配色，戏剧性明暗对比光影，华丽纹章/纹饰元素，3D浮雕金色大字标题，竖版9:16宣传海报",
                "best_for": "历史人物传记概念海报、皇室/帝国/王朝题材宣传、历史剧先导海报、史诗人物志封面、BBC/HBO历史剧风格视觉",
                "tips": "核心要素：①多层复合构图是灵魂——右上方巨型半透明侧面半身像（ghost portrait bust，单侧暖金光照射，融入云层）+ 画面中央全身高糊/远景人物（精细全身立像，手持权杖/宝剑等权力象征物）②背景场景要对应时代/地域——圣彼得堡巴洛克宫殿+帆船（俄罗斯）、凡尔赛宫殿+花园（法国）、紫禁城+长城（中国）等③底部大字标题：3D浮雕金色大写字母（filigree scroll ornamentation，顶部居中小皇冠），两行结构（CATHERINE / THE GREAT）④标题下方手写体tagline（如I'M GONNA BE / QUEEN OF MY DESTINY）⑤最底白色全大写副标语（角色定位/时间线/叙事弧）⑥纹章/纹饰元素：双头鹰/玫瑰/龙等国家/王朝纹章，置于中央人物下方⑦配色：rich gold(#D4AF37)+deep royal blue(#1B2A4A)+cream/ivory(#FFFFF0)+charcoal grey(#36454F)+warm golden highlights⑧光影：戏剧性明暗对比（chiaroscuro），暗色暴风云+金色阳光破云穿透，打亮人物一侧面部⑨水面/海浪作为底部前景框架——浪花拍打人物裙摆/脚部⑩竖版9:16 ⑪文字必须在prompt中逐条写出内容、位置、字体风格 ⑫不要只堆'cinematic epic'，要具体写出构图层次和每层内容",
                "example": "Style: Hollywood historical epic biopic promotional poster, vertical 9:16 format. Multi-layered cinematic composition: (1) Upper right: giant semi-translucent profile bust portrait of the subject, facing right, single-side warm golden sunlight illuminating one half of the face, other half in soft shadow, hair and crown partially dissolving into dramatic storm clouds — this is a 'ghost portrait' element, not a solid figure. (2) Center foreground: full-body standing portrait of the subject in ornate period royal attire, looking slightly upward with resolute expression, holding an ornate golden scepter, wearing ermine-trimmed royal cloak over shoulders, royal order sash across chest, small crown on styled hair. (3) Background: period-appropriate architecture on one side (baroque palaces with gilded onion domes, fortress spires, sunlight breaking through clouds behind buildings), period ships on the other side (18th-century sailing ships with imperial flags on choppy dark water). (4) Bottom: churning dark blue-grey seawater with waves crashing around the subject's feet. Color palette: rich polished gold (#D4AF37), deep royal blue (#1B2A4A), cream/ivory (#FFFFF0), dark charcoal grey (#36454F), warm golden highlight tones. Lighting: dramatic chiaroscuro — dark moody storm clouds contrasted with bright sunlit sections breaking through. Typography at top-left: small white uppercase serif text (character name, dates, narrative taglines), all-caps. Center: heraldic crest/coat of arms of the dynasty. Bottom: massive ornate 3D polished gold uppercase title with filigree scroll ornamentation and small crown above, two-line structure. Below title: gold handwritten-script tagline. Very bottom: small white uppercase taglines (role descriptors, timeline, narrative arc). Overall tone: grandeur, power, regal authority, epic historical drama. No watermark."
            },
            "ACG角色史诗海报": {
                "style_instruction": "ACG/动漫/游戏角色史诗宣传海报，多层复合构图（近景大头肖像+全身动态+舰队/建筑背景），通缉令/悬赏令式头图文案区，金色暖调+暗色风暴对比，金属刻痕质感大字标题，竖版9:16电影级海报",
                "best_for": "动漫/游戏/ACG角色概念宣传海报、通缉令/悬赏令风格角色海报、热血番先导视觉、角色史诗级Fan Art、ACG角色封神图",
                "tips": "核心要素：①多层复合构图——画面上1/3为角色超近景侧面/半侧大头肖像（backlit golden-hour lighting，rim light勾勒轮廓，融入云层/光效），画面中央为角色全身动态姿态（冲向镜头/战斗/跃起等动感姿势，表情与上方肖像形成情绪反差——上方严肃/下方狂野兴奋）②背景场景对应角色世界观——海盗舰队+海洋（海贼王）、忍村+火影岩（火影）、东京铁塔+雨夜屋顶（柯南）等③左上角通缉令/档案式头图文案区：WANTED/TARGET/FILE等大字标题+角色名+身份+名言/台词，竖排或斜排④右上方飘扬组织/阵营旗帜/徽章⑤底部大字标题：金属刻痕/战损质感3D大写字母（scratched worn-metal finish），两行结构，字母中可融入角色剪影或标志物（LUFFY的U中嵌入路飞背影）⑥标题下方手写体tagline（角色宣言/梦想/口头禅，金色brush font）⑦最底部小字区：日语+英文双语角色信息⑧配色：warm gold/orange+dark storm blue+character signature color（红色/蓝色等）+wood/worn brown⑨光影：golden-hour逆光+lens flare+dark storm云层对比，飘浮光粒/火花/尘埃效果⑩水面/波浪/风/能量波等动态前景元素⑪竖版9:16 ⑫文字必须在prompt中逐条写出内容、位置、字体风格 ⑬ACG角色的标志性特征（伤疤/发型/帽/眼镜/服装细节）必须明确列出【3D立体深度关键技巧——区分flat和光栅级立体感】⑭鱼眼/广角透视：角色冲向镜头时，前臂/拳头/脚部要明显放大+动态模糊，身体居中锐利，腿部/后方元素远去模糊——用\"extreme wide-angle/fisheye perspective distortion\"描述⑮前景遮挡层：必须有大尺寸虚化元素（雨滴/水花/碎片/粒子）覆盖在角色和标题前面，用\"IN FRONT OF EVERYTHING\"强调层级⑯背景大气透视：远景要有明显的柔焦+去饱和处理，用\"atmospheric perspective (slightly desaturated, softer focus)\"推动纵深⑰3D挤出标题：标题文字要有厚度感（thick front face + visible dark shadow sides creating block-letter 3D extrusion），用\"polished silver-steel/3D extrusion/block-letter\"描述⑱镜头互动效果：水花溅到镜头上、水滴折射彩虹prism、镜头水痕——用\"water droplets hitting the lens with water-streak lens effects on the foreground glass\"描述⑲头层肖像用\"sandwich effect\": 云层/粒子在肖像前面穿过（passing IN FRONT of portrait edges），制造夹心式深度。这5项全做到=9/10深度，缺任何一项都会显得flat",
                "example": "Style: Hyperrealistic cinematic ACG character epic promotional poster, vertical 9:16 format. Multi-layered composition: (1) Upper 1/3: massive close-up profile portrait of character, facing right, backlit by golden sunlight breaking through dramatic cloud cover, rim lighting outlining hair/accessories. Serious, resolute expression. Character signature items visible (hat, scar, goggles, etc). (2) Center midground: dynamic full-body action shot of same character rushing toward viewer in explosive pose, grinning wide with intense eyes, wearing iconic outfit, leaping over turbulent water/terrain with environmental effects (water spray, debris, energy particles). (3) Background: scene-appropriate environment — fleet of ships on choppy ocean / futuristic cityscape / fantasy landscape / urban nightscape — with dramatic sky (dark storm clouds + golden sunset glow). (4) Bottom: churning water/energy waves splashing around character feet. Top-left: wanted-poster style text block — 'WANTED' header in large serif font, character name and title below, jolly roger/faction emblem icon, thematic quote from series. Upper right: faction flag/banner waving. Bottom: massive textured 3D gold/steel title letters (scratched worn-metal finish), two-line structure with character silhouette cut into a letter. Below title: handwritten brush-style gold tagline with character dream/declaration. Very bottom: small Japanese + English bilingual text. Color palette: warm golds/oranges, dark storm blues, character signature accent color. Lighting: golden-hour backlight, lens flare, dark/light contrast, floating spark/ember/dust particles. Hyperrealistic rendering of anime/manga character. No watermark."
            },
            "裸感3D手办海报": {
                "style_instruction": "裸感3D手办浮出海报——中心角色渲染为高精度3D手办/手办质感，像物理实体从平面2D背景中飘出来（pop-out），通过两个关键技巧实现立体分离：①全身发光轮廓线（glowing rim outline）②投射阴影到背景上（drop shadow on background）",
                "best_for": "ACG角色立体展示海报、手办收藏风海报、光栅3D lenticular效果海报、角色pop-up book风格、盲盒/潮玩风格角色海报",
                "tips": "核心要素：①【最重要】两个必备视觉技巧必须同时存在——TRICK 1全身发光轮廓线：角色整个剪影必须有明亮蓝白色霓虹发光描边（2-3px宽+5-8px柔光扩散），像PS选区描边+外发光，在角色与深色背景交界处最亮；TRICK 2投射阴影：角色向下方偏移10-15px投射柔和阴影（模糊15-20px），阴影必须投射到背景上（天空/云/建筑），而不仅仅是脚下地面②角色渲染为3D手办质感：光滑vinyl/塑料皮肤表面、光泽材质衣物、镜面反射眼镜片、橡胶光泽鞋子——每件物品有不同material response③背景必须是故意扁平的2D插画/绘画风格（与3D角色形成反差），用'flat illustrated painting/artwork style, NOT 3D'强调④角色有清晰的硬边缘cutout（绝对不能柔化/羽化/大气融合）⑤3点光照：key light upper-left + blue-white rim light from behind（产生发光轮廓）+ warm fill from below⑥前景可加大尺寸虚化水滴/粒子覆盖在角色前面（IN FRONT of the 3D figure），证明角色在镜头和背景之间⑦标题文字也可做3D挤出效果+霓虹描边，但角色发光轮廓和阴影是第一优先级⑧【通道选择关键】volcengine(doubao-4)实测无法可靠执行发光轮廓和投射阴影（即使多次明确prompt仍2/10），dragoncode(gpt-image-2)首次尝试即可9/10。裸感3D效果必须用dragoncode通道",
                "example": "Style: Anime cinematic promotional poster with 'naked 3D figurine pop-out' effect. The central character is rendered as a physical 3D vinyl figurine floating IN FRONT of a flat 2D illustrated background. CRITICAL: The character entire silhouette has a bright blue-white neon glow outline (2-3px wide, soft outer glow 5-8px) tracing around their complete body — hair, head, arms, torso, legs, everything. A soft dark drop shadow (offset 10-15px downward, blurred 15-20px) is cast below the character onto the flat 2D background art (visible against sky/clouds/buildings). Character has smooth vinyl figurine texture with glossy surface properties, clean sharp cutout edges with NO feathering or atmospheric blending. Background is deliberately flat 2D anime painting style — painted illustrations, NOT 3D rendered. 3-point volumetric lighting on character only: key light from upper-left, blue-white rim light from behind, warm fill from below. Foreground: large out-of-focus water droplets on camera lens passing IN FRONT of the character. The effect should look like a premium lenticular 3D holographic card or pop-up book. Vertical 9:16 format."
            },
            "手绘水彩路线攻略图": {
                "style_instruction": "手绘水彩+水墨融合风格的自驾/徒步路线攻略信息图海报，牛皮纸/古纸质感底纹，水彩晕染山水背景，路线+站点+海拔+行程+注意事项全信息覆盖",
                "best_for": "公路旅行攻略图（318/219/66号公路等）、徒步路线图、pilgrimage朝圣路线、骑行路线规划、旅游收藏级海报、自驾俱乐部纪念品",
                "tips": "核心要素：①底纹质感是关键——warm parchment/aged cotton paper texture，subtle fiber patterns，vignette darkened edges，faint coffee-stain marks，不能像白纸打印②水彩画媒介：Traditional Chinese watercolor(水彩)+light ink wash(水墨)fusion——颜色自然晕染bloom，笔触visible③背景全景：路线经过的最具代表性的地貌景观作为全出血背景（left-to-right连续变化），用soft-focus atmospheric perspective（近处鲜艳远处模糊）④路线用醒目虚线/实线标注（terracotta red主线+blue支线+green回程线），站点用彩色圆点pin+中文标签⑤每个重要站点配手绘mini-illustration（城市地标/自然景观/文化元素）⑥海拔剖面图（小图表）用色标表示安全等级（green<2500m/yellow2500-4000m/red>4500m）⑦危险标记图标（⚠️高反/无加油站/路况/无信号）⑧底部：左侧每日行程D1-Dn，右侧出行须知icon list⑨可选支线用蓝色虚线⑩签名视觉元素（hero element）：全图最壮观的地标作为最详细的手绘插画⑪色板：terracotta red(#C1440E)+warm amber(#E8A317)主色，emerald greens+earth browns+snow whites+deep cobalt blue风景色，warm cream(#F5E6C8)纸底⑫文本用rich black(#2C1810)，可读性优先⑬信息密度高但要层次清晰——用icon+色块+分区避免杂乱⑭所有站点距离/海拔/时间信息在prompt中逐条列出，否则AI会编造数据【横向全景变体·21:9】长线性路线（如G219全程10,000km+）必须用横向21:9比例而非竖版9:16，从左到右一字排开。跨多省路线可用颜色编码标注省界（如绿=新疆/蓝=西藏/橙=云南/红=广西）。【⚠️致命坑：AI把线性路线画成圈/环线】实测发现AI对地理有刻板印象（尤其西藏/高原→AI倾向画成环线）。修复：在prompt中至少3处用CRITICAL强调'STRICTLY LINEAR, NEVER a circle/loop'，用'like a timeline/scroll/sentence'比喻。V1画成圈→V2修复后正确线性【超长prompt通道选择】prompt>8000字符时DragonCode(Node CLI)会卡在0%超时，必须用apimart Python API",
                "example": "Style: Premium hand-drawn watercolor illustrated route guide map poster, vertical 9:16 format. Aged parchment/cotton paper texture background with subtle fiber patterns, vignette edges, faint coffee-stain marks. Full-bleed panorama watercolor landscape of the route scenic highlights as dreamlike backdrop (painted in soft-focus atmospheric perspective). Warm terracotta-red dashed route line with colored circle pin markers at each labeled stop, each accompanied by a hand-drawn mini-illustration of local landmarks/culture. Hand-drawn compass rose, vintage typography. Altitude profile chart with color-coded safety zones (green/yellow/red). Day-by-day itinerary at bottom-left, travel essentials icon list at bottom-right. Optional branch routes in dashed blue. Color palette: terracotta red route, warm amber accents, emerald/alpine greens, earth browns, snow whites, cobalt blue lakes, golden ochre monasteries on cream parchment base. Text in rich dark brown/black for legibility. All route information (distances, altitudes, stops) specified precisely in prompt. No watermark. Premium museum-quality art print aesthetic."
            },
            "Apple自然科普海报": {
                "style_instruction": "Apple Keynote风格自然科普海报，纯白极简背景，主体动物极度放大占画面50-70%，高级产品摄影质感，底部四列极简icon信息栏，整体像Apple发布会视觉",
                "best_for": "动物/植物/昆虫科普海报、自然博物馆展示、生物科普社媒图、稀有物种科普",
                "tips": "核心要素：①纯白/极浅灰背景，大量留白 ②主体动物必须极度放大，占画面50-70%，成为最强视觉中心 ③主体要有真实阴影，像高级产品摄影一样立在画面中 ④主体姿态要有展示性/力量感/识别度 ⑤可保留少量必要承托物（树枝/岩石/雪地），但必须简洁 ⑥顶部左侧：中文大标题(物种名)+副标题(物种定位)+细短横线+英文名+分布信息 ⑦底部四列极简信息栏：细线icon+彩色小标题+1-3行短说明，栏目间极细浅灰竖线分隔 ⑧最底部居中灰色小字总结 ⑨色彩克制：背景纯白，主标题黑色/深石墨色，正文灰色，底部小标题可用低饱和强调色（暖棕/冷蓝/松石绿/紫/橙）⑩禁止：淡黄旧纸背景、圆角卡片、厚边框、大面积装饰图形、儿童科普风/卡通风 ⑪主体纹理必须可信（毛发/鳞片/甲壳/羽毛/斑纹）⑫竖版9:16",
                "example": "Style: Apple Keynote-style premium nature science poster, pure white minimalist background with generous white space. Ultra-high-resolution photorealistic animal subject occupying 50-70% of frame, studio product photography lighting with soft realistic shadow beneath. Top-left: large bold black Chinese species name title, grey subtitle, thin horizontal rule, small grey English name and distribution info. Bottom: four-column ultra-minimal info strip with thin line icons, small low-saturation colored titles, 1-3 line descriptions, separated by hairline grey dividers. Bottom center: small grey summary sentence. No cards, no rounded corners, no decorative borders, no yellowed paper, no cartoon style. Clean, premium, restrained, high-impact. Vertical 9:16."
            },
            "收藏手办产品海报": {
                "style_instruction": "拟真棚拍式收藏手办概念海报，暗色实景虚化背景+极浅景深，手办本体占画面70%为核心绝对视觉中心，军工产品说明书式极简无衬线文字排版，低饱和工业硬核配色，手办底座压住画面底部",
                "best_for": "ACG/游戏/动漫角色收藏手办概念海报、1/7-1/10比例手办宣传图、潮玩盲盒产品海报、机甲/装甲手办发布概念图",
                "tips": "核心要素：①【背景】拟真棚拍实景虚化——压暗处理的场景（雨夜街头/废墟/仓库等），极浅景深完全虚化，只保留散景光斑(bokeh)，不画纯白/纯黑背景②【主体】手办本体占画面70%中下部，绝对视觉中心。手办质感必须拟真——PVC/合金涂装、关节旧化磨损、漆面颗粒、布料纹理、皮肤质感，达到以假乱真③【姿态】不要呆板站姿——要有叙事感的动态/互动姿态（人物扶机甲/跨步/转身等），角色之间要有呼应④【底座】水平手办底座压住画面下沿，稳定构图重心。底座有丝印标识（单元编号/品牌名）⑤【文字排版】军工产品说明书式极简无衬线排版：左上左对齐（小字系列名→超大粗体主标题→黄色底黑字单元编码→白色竖线分隔的规格说明），右上右对齐（细白框系列编号+比例/序号/属性）。全部用硬朗工业无衬线字体⑥【配色】高对比低饱和工业色——灰白/炭黑/哑光灰占90%，功能点缀色极少（暖黄=编号/警示条，冷蓝=标识，橙白=医疗）。完全不要高饱和艳色⑦【文字颜色】只有黑/白/黄三色，信息克制不抢主体⑧【品牌元素】品牌logo可出现在机甲/臂章/底座等处，形成反差萌⑨【约束】no anime-style rendering on the figure itself, hyper-realistic physical product photography feel, shallow depth of field, bokeh background",
                "example": "Style: Premium collectible figure product concept poster, photorealistic studio photography aesthetic. Dark moody background scene (rainy night city street / industrial ruin / warehouse) with extremely shallow depth of field — background completely blurred into bokeh light spots, foreground ground with subtle wet reflective texture. The collectible figure (1/7-1/10 scale PVC/ABS/statue) dominates 70% of the frame center-bottom, rendered with hyper-realistic physical product texture: visible paint grain, weathering on joints, material-accurate surfaces. Dynamic narrative pose — not standing stiffly. Horizontal display base anchoring the bottom edge with silkscreen unit number and brand name. Typography: military spec-sheet style minimal sans-serif, left-aligned top-left (small series name → large bold main title → yellow-background black-text unit code → white-pipe-separated specs), right-aligned top-right (thin white-framed series number, scale, edition info). Color palette: desaturated industrial greys, charcoal blacks, warm yellow accent for codes, cold blue for secondary identifiers. All text in black/white/yellow only. No high-saturation colors. Vertical 9:16 format. Must look like a real premium figure product photo, not an illustration."
            },
        }
    },
    "商业科普": {
        "description": "面向职场/商业/管理者的科普漫画信息图——把抽象To B概念通俗化，用漫画分镜+流程图+对比表可视化",
        "styles": {
            "商业科普漫画信息图": {
                "style_instruction": "竖版长图商业科普漫画信息图，深藏青科技底色+白色内容卡片，IP主讲人（商务写实风）贯穿全图串联讲解，漫画分镜+逻辑流程图+对比表混合信息结构，总-分-总线性叙事（提出问题→具象化→解法→强化→总结），适配移动端滑动阅读",
                "best_for": "企业AI转型科普、ToB产品方法论解读、职场管理知识科普、行业趋势分析可视化、商业概念通俗化解读、技术方案宣讲长图",
                "tips": "核心要素：①【底色/卡片】外层大背景=低饱和深藏青(#1A2332)，叠加极低透明度线描科技元素（电路板走线/聊天气泡/芯片图标仅氛围铺垫），内容区块=纯白圆角卡片+淡灰分隔线+极淡投影浮起感②【配色体系】主色=深藏青(专业/科技)，强强调色=正红色(警示/误区/重点)，正向辅助色=清新草绿(正确路径/完成状态)，插图辅色=低饱和马卡龙色(人物服饰/家具)③【IP主讲人】贯穿全图的核心讲解人——商务写实风（非低幼夸张），短发西装职业形象，表情随内容变化（皱眉/认真/自信/鼓励），用标准对话气泡讲口语化台词，相当于面对面讲解④【叙事结构·总-分-总】开篇=大标题+IP抛出核心误区→误区演示=单格办公室场景漫画具象化问题→解法=编号步骤(1/2/3)每步左流程图+右文字说明→对比强化=左右清单对照表(红叉绿对)→收尾=总结升华+署名⑤【流程图设计】每步自带动向闭环流程图：A→B→C箭头连线，图标统一线描风格，读者不看文字也能理解流向⑥【类比具象化】用实物图标类比抽象概念（跑鞋→马拉松、蒸馏器→知识加工）大幅降低认知成本⑦【文字层级】大标题=超大粗黑体(核心词红色加粗) → 二级标题=蓝底白字圆形数字标+粗黑体 → 正文=常规无衬线中黑体(行高宽松) → 金句=加粗双引号+引用框/对话气泡 → 强制重点=红底白字标签⑧【竖版长图】适配手机滑动阅读，区块边界清晰不串读⑨【前后呼应彩蛋】收尾元素呼应开篇类比/核心概念，扣题+亲和力⑩约束：no childlike cartoon style, maintain business professionalism, all text explicitly specified in prompt",
                "example": "Style: Vertical long-form business science-pop comic infographic, mobile-scrolling optimized. Overall frame: deep navy blue background (#1A2332) with ultra-low-opacity tech line-art overlay (circuit traces, chat bubbles, chip icons) as atmospheric texture only. Content sections: pure white rounded cards with thin grey dividers and soft drop shadows, floating above the dark background. Top: large bold title with key warning phrase in red. Core IP narrator: realistic business-style漫画 character in suit,贯穿全图串联讲解, expressions changing with content (concerned, serious, confident, encouraging), speaking in speech bubbles with colloquial tone. Narrative flow: (1) Opening — title + IP states core misconception. (2) Problem visualization — single-panel office scene comic showing the wrong approach. (3) Solution — numbered steps (1/2/3), each with left-side flow diagram (A→B→C arrow-connected, uniform line-art icons) and right-side text explanation. (4) Contrast — left-right comparison checklist with red crosses and green checkmarks. (5) Closing — summary + author signature. Color system: navy blue (professional/tech), bright red (warnings/errors/emphasis), fresh green (correct/success), muted pastel (character clothing). Typography hierarchy: extra-large bold title (key word in red) → step headers (blue-circle white-number + bold) → body text (regular sans-serif, generous line-height) → key quotes (bold quoted text in speech/reference bubble) → forced emphasis (red-background white-text label). Analogies visualized as concrete icons (running shoe for marathon metaphor, distiller for knowledge processing). Vertical long image, clean section boundaries. Must feel like a real business consultant explaining face-to-face — professional but approachable, not childish."
            },
        }
    },
    "UI界面设计": {
        "description": "App截图、Web界面、Dashboard、交互设计稿——像真实产品的高保真界面图",
        "styles": {
            "iOS应用界面": {
                "style_instruction": "iOS App高保真界面截图，iPhone刘海屏，底部Tab Bar，Apple HIG设计规范",
                "best_for": "App Store截图、产品设计展示、UI概念稿",
                "tips": "核心要素：①明确平台（iOS）+屏幕比例 ②写清布局结构（Tab Bar/卡片流/列表）③主色/强调色要指定 ④文字必须写死内容，否则乱码 ⑤约束：readable text, proper spacing, no placeholder",
                "example": "Style: High-fidelity iOS app screenshot, iPhone frame with notch, bottom tab bar navigation. Clean Apple HIG design language. Primary color [X], accent color [Y]. Card-based layout with clear visual hierarchy. Text must be readable Chinese/English as specified."
            },
            "Dashboard数据看板": {
                "style_instruction": "数据Dashboard界面，深色主题，图表卡片布局，侧边栏导航，实时数据可视化",
                "best_for": "后台管理系统、数据分析平台、SaaS产品界面、运维监控大屏",
                "tips": "核心要素：①深色/浅色主题要明确 ②写清图表类型（折线图/柱状图/饼图/热力图）③侧边栏+顶栏+主内容区三段布局 ④数据卡片要有具体数字（不能空白）⑤约束：no placeholder charts, realistic data values",
                "example": "Style: Professional data dashboard interface, dark theme with glowing accent colors. Left sidebar navigation, top header bar with user avatar, main content area with 4 KPI cards at top and 2 large chart panels below. Line chart, bar chart, donut chart visible. Clean data visualization aesthetic. All text readable."
            },
            "Web落地页": {
                "style_instruction": "现代Web产品落地页，大Banner+功能展示+CTA，响应式设计感",
                "best_for": "产品官网、SaaS落地页、创业项目首页、营销活动页",
                "tips": "核心要素：①写清页面结构（Hero区/功能卡/评价区/CTA）②Hero区要有标题+副标题+主图+CTA按钮 ③功能展示区用icon+标题+描述卡片 ④配色和排版风格要指定 ⑤16:9或9:16都可以",
                "example": "Style: Modern SaaS product landing page, clean white background. Hero section with large headline, subtitle, and primary CTA button. Below: 3 feature cards with icons. Further: testimonial section with avatars and quotes. Professional web design, generous whitespace, modern sans-serif typography."
            },
        }
    },
    "商品与电商": {
        "description": "电商主图、产品展示、商品详情——电商平台可直接用的商品图",
        "styles": {
            "电商主图": {
                "style_instruction": "电商产品主图，纯色/渐变背景，商品居中悬浮，专业棚拍质感，卖点角标/标签",
                "best_for": "淘宝/京东主图、电商Banner、商品列表图、促销活动图",
                "tips": "核心要素：①材质和光影是灵魂——指定磨砂/金属/丝绸等质感 ②灯光要写具体（柔光箱/轮廓光/侧光）③商品角度（3/4侧/正面/俯拍）④文案只给核心1-2句（新品/限时/特价），字多了画面毁 ⑤约束：commercial photography quality, hyper-realistic textures",
                "example": "Style: Premium e-commerce hero image, clean gradient background. Product floating at 3/4 angle with sharp rim light on edges, softbox overhead lighting. Hyper-realistic material rendering — [specific material: matte black finish / brushed metal / frosted glass]. Minimal text badges: [badge copy]. Commercial photography quality."
            },
            "生活方式场景图": {
                "style_instruction": "商品生活方式场景图，商品融入真实使用场景，自然光，生活气息",
                "best_for": "商品详情页场景图、品牌社媒配图、生活方式营销",
                "tips": "核心要素：①场景要匹配商品（咖啡→书房桌角，运动鞋→城市街头）②商品要突出但不是唯一焦点 ③自然光+浅景深 ④人物使用互动更生动 ⑤约束：product clearly visible and recognizable",
                "example": "Style: Lifestyle product photography, [product] placed in a [cozy modern living room / sunny kitchen counter / urban street]. Natural window light, shallow depth of field. Warm, inviting atmosphere. The product is clearly visible and the focal point of the composition."
            },
            "食品美食摄影": {
                "style_instruction": "专业美食摄影，俯拍/45°角，道具搭配，自然光或影棚柔光，食物纹理细节丰富",
                "best_for": "餐厅菜单图、食品电商、外卖平台展示、美食博主配图",
                "tips": "核心要素：①角度指定（flat lay俯拍/45°/侧面）②食物要看起来诱人——光泽/蒸汽/酱汁/配料可见 ③搭配道具（餐具/食材原料/香料/布巾）④背景要有质感（木纹/大理石/亚麻布）⑤约束：appetizing, real food texture, no plastic look",
                "example": "Style: Professional food photography, 45-degree angle shot. [Dish name] beautifully plated on [ceramic/stone] dish, garnished with [herbs]. Natural side lighting creating gentle shadows. Props: wooden cutting board, fresh ingredients scattered artfully, linen napkin. Warm color temperature, appetizing presentation."
            },
            "手作小物氛围产品图": {
                "style_instruction": "手作/文创小商品的氛围产品摄影，暖色调虚化光斑背景（串灯/烛光bokeh），浅景深聚焦产品细节，真人手部持握展示产品比例，柔暖方向光突出材质纹理（织布/金属/塑料光泽）",
                "best_for": "钥匙扣/手机壳/手办/文具等小商品氛围展示图、手作品牌商品图、文创产品社媒配图、电商详情页氛围图",
                "tips": "核心要素：①【背景】暖色暗底+散景光斑（bokeh），像串灯/烛光/节日灯泡虚化成圆形金色光点，营造温馨氛围②【景深】极浅景深，只有产品和手部清晰，背景完全虚化③【持握展示】真人手从画面边缘入镜持握/托举产品，展示产品实际比例（8-10cm等），手指细节可见④【材质表现】柔暖方向光照亮产品每个材质——织物的编织纹理、金属的光泽反射、塑料/树脂的光滑表面⑤【色调】暖金+深棕+暗红基调，产品原色保持准确⑥【构图】产品居中偏下，手从上方或侧面入镜，不喧宾夺主⑦参考图见 assets/keychain_product_lifestyle.jpg",
                "example": "Style: Warm atmospheric product photography of a small handmade craft item, held by a person's hand entering from the edge of frame. Shallow depth of field — only the product and hand are in sharp focus. Background is completely blurred with strong bokeh effect: warm dark brown/near-black base scattered with soft round golden-yellow out-of-focus lights resembling string lights or candlelight. Soft warm directional lighting highlights every material texture — woven fabric grain, polished metal shine, glossy surfaces. Cozy, inviting, premium handmade aesthetic. The hand provides real-world scale reference. No watermark, no text overlay."
            },
        }
    },
    "建筑与空间": {
        "description": "建筑效果图、室内设计、空间可视化——像专业建筑事务所出的渲染图",
        "styles": {
            "现代室内设计": {
                "style_instruction": "现代室内设计效果图，写实渲染质感，自然光+人工照明，材质细节丰富",
                "best_for": "室内设计方案、家具展示、家装营销、Airbnb房源图",
                "tips": "核心要素：①指定空间类型（客厅/卧室/厨房/办公室）②材质要写（混凝土/木地板/大理石/金属）③冷暖对比是作弊码——室外冷蓝+室内暖黄 ④人眼视角（eye-level perspective）避免透视变形 ⑤时间指定（白天/黄昏/夜景）",
                "example": "Style: Architectural interior visualization, photorealistic rendering quality. [Living room / bedroom / kitchen] with [materials: exposed concrete, warm timber, large glass windows]. Golden hour natural light streaming through windows, warm interior lighting. Eye-level perspective, wide-angle lens. Cool blue ambient exterior, warm orange interior glow."
            },
            "建筑外观渲染": {
                "style_instruction": "建筑外观效果图，写实渲染，环境融合，鸟瞰或人眼视角",
                "best_for": "建筑方案展示、城市规划视觉、地产营销、景观设计",
                "tips": "核心要素：①视角选择——鸟瞰(aerial)/人眼(eye-level)/仰视(low-angle) ②建筑和自然环境的关系（嵌入/对峙/融合）③时间/天气（黄昏/雨天/雪景）④周围环境（树林/城市/山体）⑤渲染质量写UE5级或V-Ray级",
                "example": "Style: Photorealistic architectural exterior visualization. [Building type: modern cabin / glass tower / traditional courtyard] nestled in [pine forest / urban streetscape / hillside]. Aerial perspective. Golden hour lighting with dramatic long shadows. UE5 rendering quality, ray tracing. Architecture harmoniously integrated with natural environment."
            },
        }
    },
    "品牌与标志": {
        "description": "Logo设计、品牌识别系统、VI视觉方案——品牌设计交付物",
        "styles": {
            "品牌Logo设计": {
                "style_instruction": "品牌Logo设计方案，纯白背景，展示Logo mark+标准字+辅助图形，扁平化矢量风格",
                "best_for": "Logo概念提案、品牌视觉方向探索、VI设计初稿",
                "tips": "核心要素：①先定义品牌关键词（innovative/minimalist/trustworthy）②Logo类型要指定（几何图形/字标/图形+字标）③纯白背景方便后期抠图 ④展示多种变体（彩色/单色/反白）⑤约束：no gradients (unless intentional), scalable vector style, pure white background",
                "example": "Style: Brand identity logo design presentation, pure white background. Logo mark: [geometric fusion description]. Clean flat vector style, high contrast. Show logo mark alone, logo mark + wordmark combination, and one application mockup. Modern corporate, minimal, scalable."
            },
            "品牌VI系统": {
                "style_instruction": "品牌VI视觉识别系统展示，含Logo/色彩/字体/应用示例的完整Moodboard",
                "best_for": "品牌全案提案、VI交付物、品牌视觉手册",
                "tips": "核心要素：①展示内容：Logo+色板+字体+3-4个应用示例（名片/信封/包装/工牌）②统一画板/展板风格 ③配色和排版要和品牌调性一致 ④约束：cohesive visual system, consistent style across all items",
                "example": "Style: Brand identity system presentation board, clean layout on neutral background. Central logo mark surrounded by: color palette swatches, typography specimens, and 4 application mockups (business card, letterhead, shopping bag, uniform). Cohesive modern visual system, all elements unified by brand color [X] and typeface [Y]."
            },
        }
    },
    "文档与出版物": {
        "description": "杂志排版、菜单设计、报纸版式、书籍封面——专业出版级版式设计",
        "styles": {
            "杂志内页排版": {
                "style_instruction": "时尚/生活方式杂志内页排版，多栏布局，大图+文字混排，编辑式设计",
                "best_for": "杂志概念稿、编辑设计提案、内容营销视觉",
                "tips": "核心要素：①明确栏数（2栏/3栏）和页边距 ②大图+文字混排比例 ③标题用衬线/无衬线要指定 ④正文用'simulated text blocks'让AI填，只写死大标题 ⑤约束：professional editorial layout, proper grid",
                "example": "Style: Fashion magazine double-page spread, 3-column grid with wide margins. Left page: full-bleed high-fashion photograph. Right page: large elegant serif headline, simulated body text blocks, pull quote with oversized quotation marks. Monochrome with [color] accents. Professional editorial typography."
            },
            "餐厅菜单设计": {
                "style_instruction": "高级餐厅菜单设计，优雅排版，分类清晰，菜品名+描述+价格层次分明",
                "best_for": "餐厅菜单视觉稿、咖啡店饮品单、酒吧酒单、烘焙店价目表",
                "tips": "核心要素：①菜单类型（单页/折页/小册子）②分类结构（前菜/主菜/甜品/饮品）③每道菜：菜名(大)+简短描述(小)+价格(右对齐) ④配色和字体匹配餐厅调性 ⑤约束：readable prices, organized sections, appetizing descriptions",
                "example": "Style: Elegant restaurant menu design, single page vertical layout. Dark background with gold text. Sections: Appetizers, Mains, Desserts. Each item: dish name in elegant serif, short ingredient description in smaller grey text, price right-aligned. Decorative divider lines between sections. Premium dining aesthetic."
            },
        }
    },
    "场景与叙事": {
        "description": "有故事、有事件、有动势的场景概念图——不是明信片，是有叙事张力的画面",
        "styles": {
            "叙事概念场景": {
                "style_instruction": "叙事概念场景图，有明确事件/动作发生，镜头语言丰富，叙事张力强",
                "best_for": "游戏/影视概念设定、故事板、小说插图、情绪板",
                "tips": "核心要素：①必须有'动词'——写事件（正在崩塌/刚点燃/逃离中），不是静态风景 ②镜头语言指定（low angle仰拍/dutch angle倾斜/over-the-shoulder过肩）③冲突/戏剧感是关键 ④色调和氛围要匹配故事情绪 ⑤约束：narrative tension, dynamic composition, no static postcard look",
                "example": "Style: Narrative concept art scene, cinematic composition. [Specific event happening — e.g., 'the exact moment an ancient seal breaks']. Low angle shot emphasizing scale. Blinding central light casting long dramatic shadows. Awe-inspiring, terrifying atmosphere. Dynamic action frozen at peak tension. No static landscape, no peaceful postcard mood."
            },
            "氛围概念图": {
                "style_instruction": "氛围/情绪概念图，强调环境氛围和情绪感染力，电影级光影",
                "best_for": "影视前期概念、游戏氛围设定、情绪板、品牌视觉氛围",
                "tips": "核心要素：①情绪关键词3-5个（mysterious/serene/melancholic/epic）②光影是核心——指定光源类型和方向 ③环境元素要具体（雾/雨/阳光/萤火虫）④可以没有明确人物，靠环境讲情绪 ⑤约束：atmospheric, mood-driven, cinematic lighting",
                "example": "Style: Atmospheric mood concept art, cinematic lighting. [Environment: abandoned railway station at dawn]. Volumetric fog, soft diffused golden light filtering through broken glass roof. Long shadows, desaturated cool tones with warm highlights. Melancholic, mysterious, quietly beautiful. No characters needed — the space tells the story."
            },
        }
    },
    "手帐与拼贴": {
        "description": "手绘旅行日记、手帐拼贴、纪念册、Scrapbook风格——像手工制作的实体手帐被拍下来",
        "styles": {
            "旅行手帐日记": {
                "style_instruction": "翻开的旅行手帐/旅行日记拼贴页，手工制作的质感，拍立得照片+手写文字+和纸胶带+小涂鸦",
                "best_for": "旅行纪念、情侣日记、日常记录、vlog封面、小红书旅行打卡",
                "tips": "核心要素：①底色=米黄/奶白纹理纸张（#F6F0E6），带天然纸纤维纹理和泛黄旧化边缘 ②照片=拍立得/宝丽来风格（厚白边框），2-8度随机倾斜角，和纸胶带贴角 ③文字=休闲手写体（非印刷体），深炭灰（#272522），大小分级（标题>时间戳>正文） ④装饰=简单线条小涂鸦（花朵/交通图标/食物/爱心），半透明淡彩填充 ⑤和纸胶带=小条状贴照片角，图案多样（圆点/条纹/纯色牛皮纸） ⑥色彩=柔和大地色系调色盘，绝不浓烈 ⑦布局=非对称有机排版，留白自然，元素可轻微重叠 ⑧约束：must look like a real physical scrapbook page photographed flat, not a digital collage or graphic design poster",
                "example": "Style: Open travel scrapbook journal double-page spread, cozy nostalgic handcrafted aesthetic. Textured cream off-white notebook paper background (#F6F0E6) with aged worn edges and subtle natural paper grain. Instax Polaroid-style photos with thick white borders, slightly rotated at random angles, attached with small washi tape strips on corners. Casual uneven handwritten script text in soft charcoal (#272522). Tiny hand-drawn line doodles with light watercolor fills (flowers, icons, hearts, sparkles). Muted earthy pastel color palette. Hand-drawn route map on one page. Organic asymmetrical layout with natural spacing. Must look like a real physical scrapbook page photographed flat-lay, not a digital collage or graphic design poster."
            },
            "美食手帐": {
                "style_instruction": "美食探店手帐风格，餐厅评价日记页，美食照片+手写笔记+评分+小涂鸦",
                "best_for": "美食探店记录、餐厅打卡、吃货日记、小红书美食笔记封面",
                "tips": "核心要素：①同旅行手帐底色和纸张质感 ②美食照片=暖色调、近距离特写，拍立得边框 ③手写体=店名大号+菜名中号+口感评价小号 ④评分系统=手绘星星/表情符号涂鸦 ⑤装饰=手绘餐具/食材小图标 ⑥约束：warm cozy food diary feel, hand-assembled scrapbook page",
                "example": "Style: Open food diary scrapbook page, handcrafted restaurant review journal. Textured cream notebook paper. Instax-style food photos with warm appetizing coloring, white borders, washi tape corners. Casual handwritten text — restaurant name in large script, dish names medium, tasting notes small. Hand-drawn star ratings and food doodles (chopsticks, steam, chili peppers). Cozy nostalgic vibe. Real physical scrapbook aesthetic."
            },
            "情侣纪念手帐": {
                "style_instruction": "情侣恋爱纪念手帐，甜蜜回忆拼贴，照片+票根+手写情话+爱心涂鸦",
                "best_for": "纪念日、情人节、情侣日常、恋爱记录、表白/求婚创意",
                "tips": "核心要素：①底色偏暖粉米白（#FAF0F0）②照片=两人的合照+生活瞬间，拍立得风格 ③手写体=甜蜜温柔的笔迹，粉棕色墨水 ④装饰=手绘爱心、小星星、牵手涂鸦、卡通情侣小人 ⑤可加入票根/卡片/标签等实物拼贴元素 ⑥约束：romantic sweet couple memory scrapbook, warm intimate handmade feel",
                "example": "Style: Open romantic couple memory scrapbook page, handcrafted love diary. Warm pinkish cream paper background (#FAF0F0). Instax-style couple photos and candid daily moments, white borders, decorative washi tape. Sweet casual handwritten text in warm brown-pink ink. Hand-drawn hearts, stars, tiny cartoon couple doodles. Ticket stubs, cards, and small keepsake collage elements. Romantic cozy intimate atmosphere. Real physical scrapbook aesthetic."
            },
        }
    },
}
