"""Van Vo book data — 5 Vietnamese fairy tales w/ detailed prose + image prompts.

Each book follows /fk-van-vo skill rules:
- 14 story scenes (60-100 từ detailed prose, dialogue + iconic phrases)
- Image prompts get STYLE template appended by pipeline
- Motions face-safe: scene 0 = static, default static, motion only when fitting
- Slang density ~1/scene from ALLOWED list, NO banned terms, NO ad break
"""

# Reusable character/setting snippets (keep prompts shorter + consistent)
def _char(name, desc):
    return f"{name} ({desc})"

# ================ BOOK 1: THẠCH SANH ================
THACH_SANH = _char("Thạch Sanh", "young Vietnamese man, kind orphan hero: brown cargo shorts + cream solid hoodie no print, white sneakers, gold chain, undercut blonde hair, gentle confident face")
LY_THONG = _char("Lý Thông", "middle-aged scheming Vietnamese man: black bomber jacket solid no print + dark jeans, aviator sunglasses, slick black hair, sly smirk")
CONG_CHUA = _char("Princess công chúa", "young Vietnamese princess: pastel pink áo dài with white Air Force sneakers underneath, long black hair, gold hair pin, gentle elegant pose")
TRAN_TINH = "Trằn Tinh giant monster: scaly dark green skin, sharp white fangs, glowing red eyes, massive serpentine body, terrifying"
VUA = _char("Vietnamese king", "elderly with red royal robe + aviator sunglasses + Apple Watch, white beard")
DAI_BANG = "Đại bàng giant black eagle: massive wingspan, glowing golden eyes, sharp talons"
VUA_THUY_TE = "Vua thủy tề aquatic king: blue flowing robes with sea pearls, crown of coral, long silver beard"

THACH_SANH_BOOK = {
    "slug": "thach-sanh",
    "title": "Thạch Sanh",
    "story_summary": "Văn Vở Gen Z phong cách. Thạch Sanh — chàng trai mồ côi tốt bụng, bị Lý Thông lừa đảo, vẫn thắng cuối cùng. Phiên bản giải nén kiểu phim Captain America First Avenger.",
    "scripts": [
        # Scene 1 (Hook short — chào + giới thiệu truyện, ~14s)
        "Trong kho tàng cổ tích Việt Nam, có một câu chuyện về chàng trai hiền lành bị lừa nhiều lần nhưng cuối cùng vẫn thắng. Phiên bản chi tiết của truyện Thạch Sanh, anh em ngồi vững mà thưởng thức nha.",
        # Scene 2 (Hook short — plot tease, ~14s)
        "Câu chuyện có chằn tinh ăn thịt người, đại bàn bắt công chúa, cây đàn thần kỳ diệu, và sét trời đánh kẻ phản bội. Đầy đủ drama, đầy đủ bài học, dân chơi mới hiểu được hết các tầng ý nghĩa sâu sắc.",
        # Scene 3 (Body 1 — Thạch Sanh tuổi thơ + movie mapping)
        "Ngày xửa ngày xưa, có chàng trai tên Thạch Sanh mồ côi cha mẹ từ nhỏ, sống một mình dưới gốc cây đa cổ thụ. Hàng ngày anh đi đốn củi kiếm ăn qua ngày, sống đơn sơ nhưng tâm hồn vô cùng trong sạch lương thiện. Một hôm có tiên ông xuống dạy anh võ nghệ và phép thuật, Thạch Sanh chăm chỉ tập luyện trở thành tráng sĩ.",
        # Scene 4 (Body 2 — Lý Thông kết nghĩa)
        "Một ngày kia Lý Thông, gã bán rượu lanh lợi gian xảo đi ngang qua thấy Thạch Sanh khỏe mạnh, thì tỏ vẻ ân cần kết nghĩa anh em. Hắn rủ Thạch Sanh về nhà ở chung, bảo coi như ruột thịt một nhà. Thạch Sanh chất phác tin lời ngay, dọn về sống cùng mẹ con Lý Thông không một chút nghi ngờ. Đâu ngờ mọi sự đều là kế hoạch scam trắng trợn để lợi dụng sức mạnh của Thạch Sanh sau này.",
        # Scene 5 (Body 3 — Chằn tinh + lừa đi thay)
        "Trong vùng có con chằn tinh hung dữ, mỗi năm dân làng phải nộp một mạng người tế thần để nó tha cho cả vùng. Năm ấy đến lượt Lý Thông phải đi nộp mạng cho chằn tinh, hắn sợ chết khiếp không dám đi. Hắn bèn lừa Thạch Sanh: em ơi anh đang bận giữ rượu, em đi cúng giùm anh được không. Thạch Sanh chân chất gật đầu, liền đi không một chút nghi ngờ, mang gậy đến đền chằn tinh.",
        # Scene 6 (Body 4 — Giết chằn tinh + cướp công)
        "Đêm khuya chằn tinh hiện ra khổng lồ, miệng phun lửa hung tợn định ăn thịt Thạch Sanh. Anh dùng võ thuật và phép thần đã học chiến đấu kịch liệt, cuối cùng chém đứt đầu chằn tinh. Thạch Sanh vác đầu quái vật về nhà khoe với Lý Thông, hắn liền nghĩ ra kế bẩn cướp công. Lý Thông bảo Thạch Sanh trốn đi vì giết chằn tinh là phạm tội, rồi vác đầu đến triều đình nhận thưởng và được làm trạng nguyên.",
        # Scene 7 (Body 5 — Đại bàng + giam hang)
        "Một thời gian sau, công chúa con vua đi dạo trong vườn thì bị con đại bàng khổng lồ bắt bay đi mất. Vua sai Lý Thông đi cứu, hắn lúng túng không biết làm sao đành lén tìm Thạch Sanh giúp. Thạch Sanh tốt bụng đồng ý theo dấu vết đại bàng đến tận hang sâu trong núi, lao xuống cứu công chúa lên. Sau khi đưa công chúa lên, Lý Thông bèn lấp miệng hang nhốt Thạch Sanh lại dưới đáy, mang công chúa về nhận công một mình.",
        # Scene 8 (Body 6 — Vua thủy tề + cây đàn)
        "Thạch Sanh dưới hang sâu tưởng đã chết oan, đi lang thang tìm đường ra thì gặp con trai vua thủy tề bị nhốt trong cũi sắt. Anh cứu hoàng tử ra ngoài và được dẫn xuống thủy cung gặp vua thủy tề. Vua tặng anh nhiều vàng bạc nhưng Thạch Sanh chỉ xin một cây đàn cũ làm kỷ niệm. Anh trở về dương gian sống ẩn dật dưới gốc đa cũ, không hề biết Lý Thông đã cướp hết công lao của mình.",
        # Scene 9 (Body 7 — Gãy đàn cứu công chúa — WITH ICONIC PHRASE)
        "Công chúa từ ngày được Lý Thông đưa về cung bỗng nhiên hóa câm, không nói được một lời nào. Vua mời bao nhiêu danh y đến chữa cũng không khỏi, ai ai cũng buồn phiền lo lắng. Thạch Sanh từ gốc đa lấy cây đàn ra gảy lên, cất tiếng hát theo: đàn kêu tích tịch tình tang, ai mang công chúa dưới hang trở về. Tiếng đàn vang vọng bay tới tận hoàng cung, công chúa nghe bỗng bật khóc và nói được trở lại, kể hết sự thật về Lý Thông cho cha nghe.",
        # Scene 10 (Body 8 — Mười tám nước + nồi cơm thần)
        "Vua biết sự thật liền truyền Thạch Sanh vào cung, gặp lại công chúa hai người mừng mừng tủi tủi. Vua xử Lý Thông tội chết nhưng Thạch Sanh tha cho vì lòng nhân từ, đuổi về quê làm dân thường. Mười tám nước chư hầu nghe tin vua gả công chúa cho người không hoàng tộc thì kéo quân sang đánh ầm ầm. Thạch Sanh mang ra niêu cơm thần ăn mãi không hết đãi quân đối phương. kèm tiếng đàn nhân nghĩa khiến cả vạn quân hổ thẹn rút lui.",
        # Scene 11 (Body 9 — Lý Thông bị sét)
        "Lý Thông và mẹ trên đường về quê tưởng đã thoát chết, đi đến giữa đồng trời quang bỗng nhiên nổi sấm sét đùng đùng. Sét đánh trúng cả hai mẹ con biến thành hai con bọ hung đen sì bò lê trên đất. Đây là quả báo cho những kẻ lừa đảo bạn bè và cướp công người khác trong giang hồ. Trời cao có mắt, ác giả ác báo không một ai thoát được dù tinh khôn đến đâu đi nữa.",
        # Scene 12 (Body 10 — Cưới công chúa + lên ngôi)
        "Sau khi giải quyết xong mọi chuyện, vua làm lễ cưới long trọng gả công chúa cho Thạch Sanh giữa muôn dân hân hoan. Thạch Sanh được phong làm phò mã rồi truyền ngôi vua, từ một anh đốn củi mồ côi nay lên đỉnh cao quyền lực. Đại boss thật sự không phải kẻ ác mưu nhiều, mà là người tốt bụng kiên trì đến cùng. Anh ngồi trên ngai vàng vẫn nhớ về gốc đa quê cũ, không một chút tự kiêu khoe khoang.",
        # Scene 13 (Body 11 — Trị vì hạnh phúc)
        "Thạch Sanh trị vì đất nước bằng lòng nhân từ và công bằng, dùng nồi cơm thần chăm lo dân chúng không ai phải đói khổ. Cây đàn thần thi thoảng được mang ra gảy giải sầu, tiếng đàn nhắc nhở mọi người sống nhân ái với nhau. Công chúa và Thạch Sanh sinh con đẻ cái, sống hạnh phúc trọn đời trong cung điện vàng son. Tiếng thơm về vị vua hiền lành lan truyền khắp mười tám nước chư hầu và còn mãi mãi về sau này.",
        # Scene 14 (Moral)
        "Câu chuyện Thạch Sanh dạy ta rằng người tốt bụng kiên trì cuối cùng sẽ được đền đáp xứng đáng. Kẻ lừa đảo bạn bè và cướp công người khác dù tinh khôn đến đâu cũng không thoát được luật trời cao. Sức mạnh thực sự không phải ở mưu mô xảo quyệt, mà ở tâm hồn trong sạch và lòng vị tha với mọi người. Hãy sống tử tế như Thạch Sanh, dù gặp bao nhiêu thử thách cũng giữ vững niềm tin vào điều thiện.",
    ],
    "image_prompts": [
        # 1 — Hook atmospheric
        f"Atmospheric establishing wide shot: ancient Vietnamese mountain village at twilight, mist rising from rice paddies, distant pagoda silhouettes, no characters visible, mood-setting cinematic.",
        # 2 — Hook movie poster
        f"Movie-poster composition: {THACH_SANH} on LEFT half holding a wooden staff with mountains behind, {LY_THONG} on RIGHT half smirking with sly aviator pose, split lighting dramatic.",
        # 3 — Body 1 Thạch Sanh tuổi thơ
        f"{THACH_SANH} sitting cross-legged under a massive ancient banyan tree at sunrise, chopping wood with axe, simple thatched roof shack behind, peaceful rural setting with morning mist.",
        # 4 — Body 2 Lý Thông kết nghĩa
        f"Village marketplace scene: {LY_THONG} approaching {THACH_SANH} with fake friendly grin extending hand, wine jars and baskets around, blurred villagers in traditional outfits browsing market.",
        # 5 — Body 3 Chằn tinh lừa
        f"Dark night scene: {LY_THONG} pointing toward an ominous temple shrine on a hill, {THACH_SANH} listening innocently with staff, eerie red moon, cold blue ambient light.",
        # 6 — Body 4 Combat chằn tinh
        f"Epic combat scene inside dark temple: {THACH_SANH} mid-swing wooden staff toward {TRAN_TINH}, fire and blood splattering, dynamic motion blur, low-angle hero shot.",
        # 7 — Body 5 Đại bàng cave
        f"Dramatic cave scene: {THACH_SANH} descending into a deep pit on a rope toward {CONG_CHUA} held by {DAI_BANG}, glowing eyes of eagle, dark stormy clouds above the pit.",
        # 8 — Body 6 Vua thủy tề underwater
        f"Underwater mystical scene: {THACH_SANH} kneeling before {VUA_THUY_TE} in coral throne room, schools of glowing fish swimming around, cyan magical glow, traditional Vietnamese underwater palace.",
        # 9 — Body 7 Gãy đàn (iconic)
        f"Royal courtyard scene at night: {THACH_SANH} sitting under banyan tree playing an ancient wooden zither đàn, mouth singing, magical music notes glowing cyan in air flowing toward distant royal palace, soft moonlight, mystical iconic moment.",
        # 10 — Body 8 Nồi cơm thần
        f"Battle outside palace gates: thousands of foreign soldiers in armor surrounding a giant magical rice pot, {THACH_SANH} stirring pot calmly, soldiers stunned staring at endless rice, peaceful resolution.",
        # 11 — Body 9 Sét đánh
        f"Dramatic skyfall: {LY_THONG} and elderly mother running through rice paddy, massive lightning bolt striking down from black storm cloud, bright white flash, ominous mood.",
        # 12 — Body 10 Cưới công chúa
        f"Royal wedding scene: {THACH_SANH} and {CONG_CHUA} standing together on palace throne, {VUA} blessing them, warm golden lighting, courtiers in traditional outfits cheering, joyous mood.",
        # 13 — Body 11 Trị vì hạnh phúc
        f"Peaceful reign scene: {THACH_SANH} as king on golden throne with {CONG_CHUA} beside him, holding the magical đàn instrument, distributing rice from magical pot to villagers below, warm golden palace interior, grateful happy faces, prosperity mood.",
        # 14 — Moral peaceful sunrise
        f"Peaceful sunrise over ancient Vietnamese countryside: rice paddies, rivers, mountains, warm amber golden palette, less neon more contemplative oil-painting feel, hopeful resolution.",
    ],
    "motions": ["static","zoom_in","static","static","static","static","static","static","static","static","static","static","static","static","zoom_out"],
    "caption_hook": "Anh em nghe truyện Thạch Sanh kiểu phim Captain America chưa? 😱 Hero hiền lành bị lừa đảo, cuối cùng trở thành đại boss!",
    "caption_bullets": [
        "Thạch Sanh mồ côi học võ với tiên ông",
        "Lý Thông lừa đảo kết nghĩa anh em",
        "Combat chằn tinh giải cứu dân làng",
        "Đại bàng bắt công chúa, Thạch Sanh cứu nhưng bị lừa giam hang",
        "Vua thủy tề tặng cây đàn thần và nồi cơm thần",
        "Sét đánh chết Lý Thông — ác giả ác báo",
        "Cưới công chúa lên ngôi vua hạnh phúc"
    ],
    "caption_moral": "Câu chuyện dạy ta: người tốt bụng kiên trì cuối cùng sẽ thắng, kẻ lừa đảo cuối cùng phải nhận quả báo từ trời cao."
}

# ================ BOOK 2: SỌ DỪA ================
SO_DUA_HEAD = "Sọ Dừa initial form (anthropomorphic coconut shell head with face, no body, hopping along the ground): brown round head with eyes and mouth, sparkling magical energy around it"
SO_DUA_MAN = _char("Sọ Dừa transformed handsome young man", "tall handsome Vietnamese man: pastel beige solid hoodie + dark jeans, white sneakers, gold chain, undercut blonde hair, kind elegant face")
ME_SO_DUA = _char("mẹ Sọ Dừa", "elderly Vietnamese mother in simple beige áo bà ba and brown trousers, kind weathered face, hair tied in bun")
PHU_ONG = _char("phú ông", "rich middle-aged man: red áo dài with gold chains and Apple Watch, smug face with thin beard, hair slicked back")
CO_UT = _char("cô út kind youngest daughter", "young Vietnamese woman: cream pastel áo dài with white Air Force sneakers, long black hair tied simple, gentle smile")
HAI_CHI = "two jealous older sisters (chị hai và chị ba): trendy pink hoodies and ripped jeans, hair with colored highlights, smirking arrogant faces"
CA_KINH = "giant sea monster fish cá kình: enormous dark blue body, sharp teeth, churning waves"

SO_DUA_BOOK = {
    "slug": "so-dua",
    "title": "Sọ Dừa",
    "story_summary": "Văn Vở Gen Z. Sọ Dừa — chàng trai dị hình bên trong là hoàng tử tốt bụng. Phiên bản giải nén kiểu phim Beauty and the Beast (Disney 2017).",
    "scripts": [
        # Scene 1 — Hook short
        "Trong kho tàng cổ tích Việt Nam, có một câu chuyện về chàng trai sinh ra trong hình hài kỳ lạ. Phiên bản chi tiết của truyện Sọ Dừa, anh em ngồi vững nha vì câu chuyện này có nhiều bất ngờ thú vị.",
        # Scene 2 — Hook short plot tease
        "Câu chuyện có người mẹ già hiếm muộn, có đứa con dị hình biết nói, có cô út tinh tế phát hiện chàng tráng sĩ ẩn giấu. Có hai chị xảo trá đẩy em xuống biển bị cá kình nuốt, drama đầy đủ.",
        # Scene 3 — Body 1: sinh ra + iconic plea + movie mapping
        "Ngày xửa ngày xưa, có một người đàn bà hiếm muộn đã già mà chưa có con. Một hôm bà đi rừng khát nước, thấy cái sọ dừa đựng đầy nước mưa liền bưng lên uống. Về nhà bà có thai, đến kỳ sinh ra một đứa con không tay chân chỉ có cái đầu tròn như quả dừa. Bà hoảng sợ định vứt đi, đứa bé bỗng cất tiếng nói: mẹ ơi con là người đấy, mẹ đừng vứt con đi mà tội. Bà nghe vậy động lòng giữ lại nuôi và đặt tên là Sọ Dừa.",
        # Scene 4 — Body 2: Sọ Dừa lớn lên đi làm thuê
        "Sọ Dừa lớn lên không có chân tay, di chuyển bằng cách lăn tròn khắp sân nhà. Dù vậy cậu rất ngoan ngoãn hiếu thảo, một hôm xin mẹ cho đi chăn trâu giúp người ta kiếm tiền. Bà mẹ ban đầu can ngăn nhưng cuối cùng đành để con đi làm thuê cho phú ông trong làng. Phú ông thấy đứa trẻ dị hình thì cười nhạo nhưng vẫn cho làm vì rẻ tiền công, không tốn bao nhiêu.",
        # Scene 5 — Body 3: thổi sáo + 3 cô mang cơm
        "Sọ Dừa chăn trâu rất giỏi, đàn trâu lúc nào cũng béo tốt no đủ, hơn nữa lại biết thổi sáo cực hay vang vọng cả vùng. Phú ông sai ba cô con gái thay phiên nhau mang cơm cho Sọ Dừa ngoài đồng. Chị hai và chị ba thấy Sọ Dừa dị hình thì kinh tởm đem cơm xa ném vội rồi bỏ chạy. Chỉ có cô út tâm hồn tinh tế nhận ra tiếng sáo Sọ Dừa quá đỗi hay, chắc không phải người tầm thường.",
        # Scene 6 — Body 4: cô út phát hiện
        "Một hôm cô út lén theo dõi, thấy Sọ Dừa lăn vào bụi cây thì biến hóa thành một chàng trai trẻ tuấn tú thổi sáo. Cô vô cùng kinh ngạc đứng lặng nhìn không nói gì, sau đó lặng lẽ về nhà giữ bí mật trong lòng. Từ đó cô đối xử với Sọ Dừa rất nhẹ nhàng tử tế, đem cơm tận nơi ân cần hỏi han. Sọ Dừa cảm động trước tấm lòng cô gái, lòng đã thầm yêu mến lúc nào không hay biết.",
        # Scene 7 — Body 5: cầu hôn + sính lễ iconic
        "Một ngày Sọ Dừa về xin mẹ đi hỏi cưới cô con gái út của phú ông làm vợ. Bà mẹ ngại ngùng đến gặp phú ông, hắn cười khẩy ra điều kiện sính lễ oái oăm: phải có một chĩnh vàng cốm, mười tấm lụa đào, mười con lợn béo, mười vò rượu tăm mới gả con. Phú ông nghĩ thế là chắc chắn Sọ Dừa không lo nổi, sẽ phải bỏ cuộc trong xấu hổ. Bà mẹ về buồn rầu kể lại, không ngờ Sọ Dừa cười bảo mẹ đừng lo, con đã có cách rồi.",
        # Scene 8 — Body 6: sính lễ đến + biến hóa thành tráng sĩ
        "Đến ngày hẹn, nhà Sọ Dừa bỗng nhiên đầy ắp người hầu mang đầy đủ sính lễ kỳ lạ. Một chĩnh vàng cốm, mười tấm lụa đào, mười con lợn béo, mười vò rượu tăm, không thiếu thứ nào. Phú ông không còn cách nào khác đành phải gả con gái út cho Sọ Dừa giữa sự cay cú của hai chị lớn. Trong đám cưới, Sọ Dừa bỗng nhiên hóa thành chàng trai tuấn tú khiến cả nhà sửng sốt mở tròn mắt ra nhìn.",
        # Scene 9 — Body 7: đỗ trạng + dặn vợ 3 vật iconic
        "Sọ Dừa và cô út sống hạnh phúc bên nhau, chàng học hành chăm chỉ rồi đi thi đỗ trạng nguyên được vua trọng dụng. Trước khi đi sứ nước ngoài, chàng dặn vợ giữ kỹ ba thứ luôn mang theo người: một hòn đá lửa, một con dao và hai quả trứng gà. Vợ ngạc nhiên không hiểu vì sao nhưng vẫn ngoan ngoãn làm theo lời chồng dặn. Hai chị nghe tin em rể đi xa lập tức nảy ra ý đồ độc ác, rủ cô út ra biển chơi thuyền lừa đảo.",
        # Scene 10 — Body 8: bị đẩy xuống biển + cá kình
        "Trên thuyền hai chị bất ngờ đẩy cô út xuống biển sâu, định cướp chồng em làm của mình. Cô út rơi xuống biển ngay lập tức bị con cá kình khổng lồ nuốt chửng vào bụng tối om. Cô nhớ lời chồng dặn liền lấy dao mổ bụng cá ra ngoài, dùng đá lửa nhóm lửa nướng cá ăn cho có sức. Hai quả trứng gà ấp được hai con gà con bầu bạn, cô sống một mình trên đảo hoang chờ chồng quay về cứu.",
        # Scene 11 — Body 9: Sọ Dừa về tìm vợ
        "Sọ Dừa đi sứ về tới nơi, hỏi vợ đâu thì hai chị lừa rằng cô út đã chết bệnh không ai cứu kịp. Chàng buồn rầu nhưng vẫn nghi ngờ vì không tìm thấy mộ vợ ở đâu cả. Một hôm chàng đi thuyền qua đảo hoang nghe tiếng gà gáy giọng quen, liền cập bến tìm xem. Gặp lại vợ trên đảo hoang, hai vợ chồng ôm nhau khóc nức nở vì tưởng đã chia cách vĩnh viễn.",
        # Scene 12 — Body 10: bữa tiệc lộ mặt 2 chị
        "Sọ Dừa đưa vợ về nhà, không nói gì cứ tỏ vẻ bình thường như chưa có chuyện gì. Chàng mời hai chị đến chơi nhà ăn tiệc, giấu vợ đứng phía sau bức màn lụa. Hai chị thấy em rể vẫn hỏi han ân cần thì mừng thầm, tưởng kế hoạch độc đã thành công hoàn hảo. Đến lúc Sọ Dừa kéo màn lộ ra cô út còn sống, hai chị xấu hổ chết điếng người mặt tái mét không nói được câu nào.",
        # Scene 13 — Body 11: 2 chị bỏ đi + sống hạnh phúc
        "Hai chị nhục nhã bỏ đi biệt tích không dám quay về làng, nghe nói biến thành chim chiền chiện hót khắc khoải đến cuối đời. Sọ Dừa và cô út từ đó sống hạnh phúc trọn đời trong vinh hoa phú quý. Phú ông cũng phải xấu hổ tự trách mình ngày xưa khinh thường người con rể tốt. Câu chuyện trở thành bài học truyền đời về việc đánh giá con người không phải qua vẻ ngoài bên ngoài.",
        # Scene 14 — Moral
        "Câu chuyện Sọ Dừa dạy ta rằng đừng bao giờ đánh giá người khác qua vẻ ngoài, bởi vì giá trị thật nằm sâu bên trong tâm hồn. Người có tâm tinh tế như cô út sẽ nhận ra được vẻ đẹp ẩn giấu, và được đền đáp bằng hạnh phúc xứng đáng. Kẻ chỉ biết nhìn vẻ ngoài và ghen tị như hai chị, cuối cùng phải nhận quả báo xấu hổ suốt đời. Hãy yêu thương con người vì tâm hồn của họ, không phải vì hình thức bề ngoài.",
    ],
    "image_prompts": [
        # 1 — Hook atmospheric
        f"Atmospheric establishing shot: ancient Vietnamese rural village at dawn, thatched houses by lotus pond, mist rising, distant mountains, no characters, peaceful mood-setting cinematic.",
        # 2 — Hook movie poster
        f"Movie-poster composition: {SO_DUA_MAN} on LEFT half handsome elegant, {SO_DUA_HEAD} small in center between them, {CO_UT} on RIGHT half gentle smiling, split lighting dramatic, fairy-tale feel.",
        # 3 — Body 1: mother drinks water + baby speaks (iconic plea moment)
        f"Mystical magical scene: {ME_SO_DUA} sitting inside a simple thatched hut holding newly born baby Sọ Dừa as a round coconut shaped head with face crying, mother's expression shifting from horror to acceptance, soft golden magical glow around baby's mouth indicating baby is speaking, oil lantern light, emotional moment.",
        # 4 — Body 2: Sọ Dừa lăn đi chăn trâu
        f"Rural countryside: {SO_DUA_HEAD} (just the head shape hopping) tending to water buffalos in rice paddies, {ME_SO_DUA} watching from doorway of thatched house, peaceful morning scene.",
        # 5 — Body 3: thổi sáo + 3 cô mang cơm
        f"Three young women carrying lacquered food trays approaching, {SO_DUA_HEAD} playing a bamboo flute under banyan tree, {HAI_CHI} disgusted and tossing rice from distance, {CO_UT} approaching gently with food bowl.",
        # 6 — Body 4: cô út phát hiện
        f"Hidden romantic scene: {CO_UT} peeking from behind bushes, {SO_DUA_MAN} (transformed handsome version) standing in a sunlit clearing playing flute, magical sparkles around him revealing his true form.",
        # 7 — Body 5: phú ông + sính lễ iconic list
        f"Wealthy estate courtyard: {PHU_ONG} sitting on throne-like chair laughing mockingly, {ME_SO_DUA} kneeling humbly with basket, magical golden hologram floating overhead showing items: a large jar of golden sticky rice, ten silk pink rolls, ten fat pigs, ten clay wine jars, mystical neon glow.",
        # 8 — Body 6: sính lễ delivered + wedding + Sọ Dừa transforms
        f"Grand wedding courtyard: {SO_DUA_MAN} (just transformed from head form) standing as handsome groom holding {CO_UT}'s hand, magical golden sparkles still around him, sính lễ items visible: golden rice jar + pink silk rolls + pigs + wine jars stacked nearby, guests stunned shocked faces.",
        # 9 — Body 7: scholar + 3 iconic items
        f"Royal palace scholar scene: {SO_DUA_MAN} in scholar robes sitting at desk handing {CO_UT} three small items: a flint stone, a knife, two eggs, gentle lighting, traditional Vietnamese palace interior, intimate farewell moment.",
        # 10 — Body 8: bị đẩy xuống biển + cá kình
        f"Tragic sea scene: small wooden boat on stormy ocean, {HAI_CHI} pushing {CO_UT} overboard into churning waves, giant {CA_KINH} jaws opening below in water, dramatic dark stormy sky, terrifying moment.",
        # 11 — Body 9: cô út trên đảo hoang
        f"Mystical island scene: {CO_UT} on small deserted island, two small chickens beside her, knife and flint stone at her feet, looking out to sea hopefully, sunset over ocean, lonely but determined.",
        # 12 — Body 10: bữa tiệc lộ mặt 2 chị
        f"Royal mansion banquet scene: {HAI_CHI} sitting at feast table laughing falsely, {SO_DUA_MAN} pulling back lavender curtain revealing {CO_UT} alive standing behind, sisters' faces of horror and shame, dramatic reveal moment.",
        # 13 — Body 11: 2 chị bỏ đi + Sọ Dừa cô út hạnh phúc
        f"Bittersweet split scene: LEFT half {HAI_CHI} fleeing village in shame transforming into two small birds chiền chiện flying away, RIGHT half {SO_DUA_MAN} and {CO_UT} sitting together happy in palace garden, warm contrast lighting.",
        # 14 — Moral peaceful resolution
        f"Peaceful resolution: {SO_DUA_MAN} and {CO_UT} standing together overlooking peaceful Vietnamese village at sunset from a hilltop, warm amber palette, contemplative oil-painting feel, hopeful mood.",
    ],
    "motions": ["static","zoom_in","static","static","static","static","static","static","static","static","static","static","static","static","zoom_out"],
    "caption_hook": "Anh em đã nghe Sọ Dừa kiểu phim Beauty and the Beast chưa? 😍 Chàng trai dị hình bên trong là hoàng tử thực sự!",
    "caption_bullets": [
        "Mẹ già uống nước sọ dừa sinh con dị hình",
        "Sọ Dừa chăn trâu thổi sáo cực hay",
        "Cô út tinh tế nhận ra chàng tráng sĩ ẩn giấu",
        "Sính lễ voi chín ngà gà chín cựa ngựa chín hồng mao",
        "2 chị ghen tị đẩy cô út xuống biển bị cá kình nuốt",
        "Cô út sống sót trên đảo hoang chờ chồng",
        "2 chị xấu hổ bỏ đi biệt tích vĩnh viễn"
    ],
    "caption_moral": "Câu chuyện dạy ta đừng đánh giá người qua vẻ ngoài, hãy nhìn vào tâm hồn để thấy giá trị thực sự."
}

# ================ BOOK 3: CÂY TRE TRĂM ĐỐT ================
ANH_NONG_DAN = _char("anh nông dân nghèo", "young farmer Vietnamese man: simple brown solid áo nâu + dirty cargo shorts, simple white sneakers, undercut hair, kind dirt-smudged honest face")
PHU_ONG_GIA = _char("phú ông tham lam", "greedy elderly Vietnamese rich man: red áo dài with gold rings and Apple Watch, fake friendly thin beard then mean expression")
CON_GAI_PHU = _char("con gái phú ông", "young Vietnamese woman in pink pastel áo dài with white sneakers, long black hair, sad gentle expression")
NHA_GIAU_KHAC = _char("groom rich rival", "smug young man: black bomber jacket + jeans + aviator sunglasses, gold chain, slick black hair, smirking arrogant face")
BUT_DEITY = _char("Bụt deity", "kind elderly Buddhist deity: white flowing robe with neon cyan glow aura, long silver beard, holding wooden staff, soft halo of golden light")

CAY_TRE_BOOK = {
    "slug": "cay-tre-tram-dot",
    "title": "Cây Tre Trăm Đốt",
    "story_summary": "Văn Vở Gen Z. Anh nông dân nghèo bị phú ông lừa, được Bụt giúp với phép thuật khắc nhập khắc xuất. Phiên bản kiểu phim Aladdin (Disney 1992).",
    "scripts": [
        # Scene 1 — Hook short
        "Trong kho tàng cổ tích Việt Nam, có một câu chuyện về anh nông dân nghèo bị phú ông lừa đảo. Phiên bản chi tiết của truyện Cây Tre Trăm Đốt, anh em ngồi vững nha vì có màn trừng phạt cực kỳ sảng khoái.",
        # Scene 2 — Hook short plot tease
        "Câu chuyện có anh nông dân chăm chỉ làm thuê 3 năm tận tụy, có ông phú ông tham lam lật mặt. Có ông Bụt từ bi ban thần chú, có cây tre trăm đốt phép thuật, có drama trừng phạt cuối siêu hay.",
        # Scene 3 — Body 1: anh nông dân làm thuê + movie mapping
        "Ngày xửa ngày xưa, có một anh nông dân nghèo sống một mình không cha mẹ vợ con. Anh đi làm thuê cho nhà phú ông trong làng để kiếm cơm ăn qua ngày, không có một xu dính túi. Phú ông thấy anh khỏe mạnh chăm chỉ liền hứa: con cứ làm thuê cho ta đủ ba năm thì ta sẽ gả con gái cho. Anh nông dân nghe vậy mừng rỡ, ra sức làm lụng từ sáng đến tối không hề dám nghỉ một ngày nào.",
        # Scene 4 — Body 2: phú ông trở mặt
        "Ba năm trôi qua, anh nông dân đã làm việc đến rạc người vì hy vọng được cưới con gái phú ông. Đến hạn anh tới xin phú ông giữ lời hứa, không ngờ phú ông trở mặt ngay lập tức không thèm nhìn. Hắn cười khẩy bảo: ta vừa gả con cho con trai nhà giàu Nguyễn ở làng bên rồi, mày đi chỗ khác làm thuê đi. Hóa ra phú ông đã âm thầm bán đứng anh để gả con cho người có tiền hơn, lừa đảo trắng trợn.",
        # Scene 5 — Body 3: bắt tìm cây tre trăm đốt
        "Anh nông dân điếng người không biết nói gì, phú ông thấy vậy cười nhạt rồi nói thêm một câu khinh thường. Nếu mày muốn cưới con tao thật, mày hãy đi vào rừng tìm cho được cây tre đúng một trăm đốt mang về làm sính lễ. Phú ông tưởng đó là điều kiện không thể nào, anh sẽ phải bỏ cuộc trong xấu hổ. Anh nông dân buồn rầu nhưng vẫn vác dao lên đường vào rừng tìm cây tre kỳ lạ ấy.",
        # Scene 6 — Body 4: vào rừng tìm không thấy
        "Vào rừng sâu, anh đi tìm khắp các bụi tre cao nhất to nhất nhưng không có cây nào đủ một trăm đốt liền nhau. Mỗi cây chỉ có khoảng ba bốn chục đốt là cùng, không hơn được. Anh thất vọng ngồi xuống gốc cây khóc nức nở vì biết mình bị lừa hoàn toàn rồi. Trời cao có mắt, công sức ba năm trời đổ sông đổ biển chỉ vì gặp phải kẻ scam chuyên nghiệp như phú ông.",
        # Scene 7 — Body 5: Bụt hiện ra
        "Đột nhiên một ông lão râu tóc bạc phơ hiện ra giữa làn sương sáng, ánh hào quang vàng tỏa khắp khu rừng. Ấy chính là Bụt, vị thần thường xuất hiện cứu giúp người tốt bụng gặp khó khăn trong dân gian Việt Nam. Bụt mỉm cười nhân từ hỏi: con gặp chuyện gì mà khóc thảm thiết giữa rừng vắng thế hả con. Anh nông dân ngước nhìn lên, lập tức quỳ xuống lạy Bụt rồi kể lại đầu đuôi câu chuyện một cách thật thà từ đầu đến cuối.",
        # Scene 8 — Body 6: Bụt dạy thần chú iconic (KHẮC NHẬP / KHẮC XUẤT verbatim)
        "Bụt nghe xong gật gù thông cảm, bèn truyền dạy hai câu thần chú thần kỳ giúp anh thoát khó. Bụt bảo: con hãy chặt đủ một trăm đốt tre rời, rồi xếp lại trên đất đọc câu khắc nhập khắc nhập, chúng sẽ tự dính liền lại thành cây trăm đốt ngay. Khi nào muốn rời ra thì đọc khắc xuất khắc xuất, cứ làm theo lời ta dặn không sai một câu nào nhé. Nói xong Bụt biến mất trong làn khói trắng, để lại anh nông dân một mình ngẩn ngơ vô cùng kinh ngạc.",
        # Scene 9 — Body 7: thử thần chú
        "Anh nông dân làm đúng theo lời Bụt dạy, chặt đủ một trăm đốt tre rời rồi xếp lại trên mặt đất. Anh hô lớn câu thần chú khắc nhập khắc nhập, lập tức một trăm đốt tre dính liền lại thành một cây tre cực dài. Anh thử hô khắc xuất khắc xuất thì cây tre lại tự động rời ra thành một trăm đốt riêng biệt như cũ. Anh mừng rỡ vô cùng, vác đốt tre về nhà phú ông để chứng minh mình đã hoàn thành thử thách.",
        # Scene 10 — Body 8: mang về bị cười nhạo
        "Đến nhà phú ông đúng lúc đám cưới đang diễn ra rộn ràng, anh nông dân vác một bó tre rời vào. Phú ông và nhà trai cùng các quan khách cười rộ lên cho rằng anh quá ngu ngốc, vác đốt tre rời mà tưởng là cây trăm đốt. Mọi người chế nhạo anh nông dân không tiếc lời, bảo cút khỏi đây kẻo làm hỏng đám cưới của con phú ông. Anh nông dân bình tĩnh nhìn đám đông một lúc lâu, rồi bất ngờ làm điều khiến cả nhà chết khiếp.",
        # Scene 11 — Body 9: hô khắc nhập, tre dính người
        "Anh nông dân hô lớn câu thần chú khắc nhập khắc nhập, ngay lập tức một trăm đốt tre bay vọt lên không. Cây tre dài thoăn thoắt cuốn chặt vào người phú ông, nhà giàu chú rể và mấy người chế nhạo anh trước đó. Họ bị tre kẹp chặt cứng đơ không thể nào cử động, kêu la inh ỏi xin tha trong tuyệt vọng. Anh nông dân khoanh tay đứng nhìn cười khẩy, đại boss thực sự lúc này chính là anh chứ không ai khác.",
        # Scene 12 — Body 10: phú ông xin tha + ký giấy
        "Phú ông hoảng sợ khóc lóc xin anh nông dân tha cho, hứa sẽ giữ đúng lời ban đầu gả con gái cho anh. Anh nông dân yêu cầu phú ông phải viết giấy cam kết trước mặt tất cả quan khách, không được phép trở mặt lần nữa. Phú ông run rẩy ký giấy ngay không dám chần chừ, ai bảo đã lừa người ta hai lần lận. Hắn còn phải xin lỗi anh trước toàn thể họ hàng làng xóm, mất hết thể diện trong phút chốc.",
        # Scene 13 — Body 11: khắc xuất + cưới
        "Anh nông dân hô khắc xuất khắc xuất giải phóng phú ông và mọi người khỏi cây tre. Đám cưới được tổ chức lại đàng hoàng, lần này chú rể chính thức là anh nông dân nghèo chăm chỉ. Con gái phú ông vốn cũng có cảm tình với anh từ lâu nên rất vui mừng, hạnh phúc mỉm cười rạng rỡ. Hai vợ chồng từ đó sống vui vẻ trong căn nhà mới, không phải lo lắng tiền bạc nữa.",
        # Scene 14 — Moral
        "Câu chuyện Cây Tre Trăm Đốt dạy ta rằng kẻ lừa đảo và phản bội lời hứa cuối cùng sẽ phải trả giá đắt. Người tốt bụng và chăm chỉ nếu kiên trì với chính nghĩa, sẽ nhận được sự giúp đỡ từ trời cao đúng lúc. Phép thuật mạnh nhất không phải khắc nhập khắc xuất, mà chính là sự thật thà và lòng kiên nhẫn của con người. Hãy giữ lời hứa với mọi người, đừng vì lợi ích trước mắt mà phản bội niềm tin của họ.",
    ],
    "image_prompts": [
        # 1 — Hook atmospheric
        f"Atmospheric establishing shot: ancient Vietnamese village at dawn, bamboo grove silhouettes, rice paddies stretching to horizon, no characters, peaceful mood-setting cinematic.",
        # 2 — Hook movie poster
        f"Movie-poster composition: {ANH_NONG_DAN} on LEFT half holding a single bamboo stick, {CON_GAI_PHU} center in pink áo dài, {PHU_ONG_GIA} on RIGHT half smirking with gold rings, dramatic split lighting.",
        # 3 — Body 1: anh làm thuê 3 năm
        f"Rural farm scene: {ANH_NONG_DAN} working hard in rice paddy under sun, ploughing with water buffalo, sweat dripping, sun setting, {PHU_ONG_GIA}'s grand estate visible in distance.",
        # 4 — Body 2: phú ông trở mặt
        f"Confrontation scene at rich man's gate: {PHU_ONG_GIA} dismissively waving hand turning back, {ANH_NONG_DAN} stunned with arms hanging, gold-trimmed estate entrance, mocking servants in background.",
        # 5 — Body 3: phú ông bắt tìm cây tre trăm đốt
        f"{PHU_ONG_GIA} pointing dramatically toward dense bamboo forest in distance, {ANH_NONG_DAN} standing humbly with bamboo cutting blade dao, ominous mood with dark trees, cold blue light.",
        # 6 — Body 4: tìm không thấy + khóc
        f"Deep dark bamboo forest: {ANH_NONG_DAN} sitting on ground crying in despair surrounded by towering bamboo stalks, mystical mist rising, scattered cut bamboo pieces around him, melancholy lighting.",
        # 7 — Body 5: Bụt hiện ra
        f"Mystical magical scene: {BUT_DEITY} appearing in glowing cyan mist before {ANH_NONG_DAN} kneeling in bamboo forest, beam of golden light from sky, Buddha-like aura, magical realism mood.",
        # 8 — Body 6: Bụt dạy thần chú (iconic moment)
        f"{BUT_DEITY} gesturing with one hand toward {ANH_NONG_DAN} demonstrating magic, glowing cyan magical text symbols floating in air representing the incantation, mystical knowledge transfer, golden sparkles, intimate teaching moment in bamboo forest clearing.",
        # 9 — Body 7: thử thần chú thành công
        f"Magical transformation scene: 100 bamboo stick pieces floating mid-air swirling with cyan magical particles assembling into one long bamboo stem, {ANH_NONG_DAN} watching in wonder, golden sparkles.",
        # 10 — Body 8: mang về bị cười nhạo
        f"Wedding scene at rich estate: {PHU_ONG_GIA} laughing mockingly at {ANH_NONG_DAN} arriving with bundle of bamboo pieces, {NHA_GIAU_KHAC} smirking beside {CON_GAI_PHU} in wedding outfit, guests laughing, mocking atmosphere.",
        # 11 — Body 9: hô khắc nhập tre dính người
        f"Magical chaos scene: long bamboo stick magically wrapping around {PHU_ONG_GIA} and {NHA_GIAU_KHAC} and several mocking guests squeezing them tight, cyan magical particles, {ANH_NONG_DAN} arms crossed watching coolly.",
        # 12 — Body 10: ký giấy xin tha
        f"{PHU_ONG_GIA} crying and signing a paper contract under duress while still wrapped by bamboo, {ANH_NONG_DAN} standing tall with arms crossed, witnesses watching in shock, dramatic indoor lighting.",
        # 13 — Body 11: khắc xuất + đám cưới
        f"Real wedding scene: {ANH_NONG_DAN} marrying {CON_GAI_PHU} in traditional ceremony, both happy smiling, {NHA_GIAU_KHAC} sneaking away in shame in background, warm golden lighting joyous mood.",
        # 14 — Moral peaceful sunset
        f"Peaceful resolution: {ANH_NONG_DAN} and {CON_GAI_PHU} together looking at sunset over bamboo grove and rice paddies, warm amber palette, contemplative oil-painting feel, hopeful mood.",
    ],
    "motions": ["static","zoom_in","static","static","static","static","static","static","static","static","static","static","static","static","zoom_out"],
    "caption_hook": "Anh em nghe truyện Cây Tre Trăm Đốt kiểu phim Aladdin chưa? 🎋 Phú ông tham lam bị trừng phạt sảng khoái!",
    "caption_bullets": [
        "Anh nông dân nghèo làm thuê 3 năm cho phú ông",
        "Phú ông trở mặt gả con cho người giàu khác",
        "Thách sính lễ cây tre trăm đốt làm khó dễ",
        "Bụt hiện ra dạy thần chú khắc nhập khắc xuất",
        "Anh chặt 100 đốt tre, hô thần chú liền lại thành cây",
        "Phú ông + chú rể bị tre dính chặt khóc lóc xin tha",
        "Cuối cùng cưới được con gái phú ông happy ending"
    ],
    "caption_moral": "Câu chuyện dạy ta giữ lời hứa và đừng vì lợi ích mà phản bội niềm tin của người khác."
}

# ================ BOOK 4: ĂN KHẾ TRẢ VÀNG ================
EM_TRAI = _char("em trai tốt bụng", "young Vietnamese farmer: simple brown solid áo nâu + dark jeans, simple white sneakers, kind humble honest face, undercut hair")
ANH_TRAI = _char("anh trai tham lam", "greedy older Vietnamese brother: red bomber jacket + ripped jeans, multiple gold chains, aviator sunglasses, slick black hair, smug arrogant face")
CHIM_PHUONG = "giant phoenix bird chim phượng hoàng: majestic body with glowing rainbow feathers (cyan + gold + magenta), gold beak, massive wingspan, mystical aura"
TUI_BA_GANG = "small woven cloth bag túi ba gang (3-handspan size)"
TUI_CHIN_GANG = "huge woven cloth bag túi chín gang (9-handspan size, oversized)"

AN_KHE_BOOK = {
    "slug": "an-khe-tra-vang",
    "title": "Ăn Khế Trả Vàng",
    "story_summary": "Văn Vở Gen Z. Hai anh em mồ côi — em hiền lành được phượng hoàng trả vàng, anh tham lam chết vì greed. Phiên bản kiểu phim The Wolf of Wall Street (2013).",
    "scripts": [
        # Scene 1 — Hook short (slang: dân chơi)
        "Hôm nay anh em sẽ nghe lại một câu chuyện cổ tích quen thuộc nhưng đầy bài học, kể về một ông anh tham không đáy và một người em hiền lành đáo để. Truyện Ăn Khế Trả Vàng, anh em ngồi vững nha vì kết thúc khá là sảng khoái cho những kẻ tham mà không biết đủ. Dân chơi mới hiểu được bài học sâu sắc đằng sau câu chuyện đơn giản này.",
        # Scene 2 — Hook plot tease (slang: drama, khét lẹt)
        "Câu chuyện có cuộc chia gia tài đầy drama giữa hai anh em ruột mồ côi. Có cây khế cằn cỗi tưởng vô dụng nhưng lại là cả gia tài, có chim phượng hoàng kỳ diệu biết nói tiếng người. Có túi ba gang khiêm tốn đối đầu túi chín gang khổng lồ, và một cái kết khét lẹt giữa biển khơi sâu thẳm.",
        # Scene 3 — Body 1: chia tài sản (slang: siêu phèn)
        "Ngày xửa ngày xưa, cha mẹ mất sớm để lại một ít gia tài cho hai anh em ruột. Người anh tham lam ngay từ nhỏ, không chia bài đến nửa miếng mà gom sạch ruộng vườn, trâu bò, vàng bạc cho riêng mình. Phần em hiền lành chỉ vỏn vẹn một cây khế cằn cỗi cùng túp lều rách nát siêu phèn ngả nghiêng theo gió. Nhưng em không hề oán trách lấy một lời, lặng lẽ dọn ra ở riêng bắt đầu cuộc sống mới với hai bàn tay trắng.",
        # Scene 4 — Body 2: em chăm khế (slang: đỉnh, idol)
        "Người em ngày đêm chăm chỉ tưới nước bón phân cho gốc khế, đồng thời đi làm thuê làm mướn để có cái ăn qua ngày. Trời thương người chăm, cây khế bỗng trổ hoa rực rỡ rồi đậu quả ngọt lịm sai trĩu cả cành, đỉnh đến mức ai nhìn cũng phải thèm. Em vui mừng chia khế cho cả xóm cùng ăn, không hề tham riêng cho mình bao giờ. Cả làng đều thương cậu em hiền lành, coi em như idol của khu vực vì lòng tốt hiếm có.",
        # Scene 5 — Body 3: chim đến (slang: lú, rén)
        "Một sáng đẹp trời, đột nhiên có một con chim cực to với bộ lông sặc sỡ óng ánh bay đến đậu trên cây khế. Em trai từ trong lều nhìn ra thì sửng sốt vô cùng, lú không biết chim quý này từ đâu mà đến. Chim ăn khế ngon lành không e dè ai, em đứng nhìn mà tim đập thình thịch vì sợ nó ăn hết cả cây. Nghĩ đi nghĩ lại, em đành rụt rè bước ra hỏi chuyện chim, giọng rén ngại ngùng không dám lớn tiếng.",
        # Scene 6 — Body 4: em than chim (slang: đại boss)
        "Em trai nhẹ nhàng cất lời với chim: chim ơi chim, ăn ít thôi để lại cho tôi với. Cả gia tài của tôi chỉ có mỗi cây khế này, chim ăn hết thì tôi biết lấy gì sống đây. Con chim ngừng mỏ, ngẩng lên nhìn em với đôi mắt long lanh hiểu chuyện đầy thấu cảm. Đột nhiên chim cất tiếng nói rõ ràng như người, khiến em trai đứng im hơi thở, hai mắt mở to ngơ ngác không tin nổi vào điều mình đang chứng kiến.",
        # Scene 7 — Body 5: chim đáp ICONIC (slang: ngon ơ)
        "Chim cất giọng rõ ràng vang xa cả góc vườn: ăn một quả trả một cục vàng, may túi ba gang mang theo mà đựng. Em trai nghe xong thì vô cùng kinh ngạc, vội hỏi đi hỏi lại đến mấy lần cho chắc chắn không nghe nhầm. Chim gật đầu xác nhận, vỗ cánh phành phạch bay đi, hẹn sáng mai quay lại đón em đi lấy vàng. Em mừng đến phát run, ngon ơ về nhà may ngay một cái túi ba gang nhỏ xinh đúng kích thước chim đã dặn.",
        # Scene 8 — Body 6: em đi đảo (slang: flex)
        "Sáng hôm sau chim đúng giờ bay đến, em trai ôm túi ba gang leo lên lưng chim bắt đầu chuyến đi xa. Chim vỗ cánh chở em vượt qua biển rộng mênh mông, bay đến một hòn đảo lấp lánh ánh kim sáng cả góc trời. Trên đảo, vàng bạc châu báu xếp chồng chất cao như núi, ai thấy cũng phải hoa mắt chóng mặt vì chói. Em trai chỉ lấy đầy đúng một túi ba gang rồi theo chim về nhà, không hề flex chuyện này với bất kỳ ai trong làng.",
        # Scene 9 — Body 7: em giúp dân (slang: idol)
        "Có vàng trong tay, em trai không hề tiêu xài hoang phí mà dành ra mua ruộng vườn giúp cả dân làng. Mọi người trong làng đều biết em đột nhiên giàu, nhưng vì em quá tử tế nên ai cũng quý mến, không một ai ganh ghét nửa lời. Em xây nhà mới khang trang nhưng vẫn sống đơn giản, hằng ngày vẫn ra chăm cây khế và chia quả cho hàng xóm như xưa. Tiếng thơm về cậu em hiền lành lan ra khắp vùng, ai cũng coi em như ai đồ của cả khu vực luôn.",
        # Scene 10 — Body 8: anh nghe + đổi (slang: scam, drama)
        "Tin em trai bỗng dưng đổi đời lan đi khắp vùng, bay đến tận tai ông anh tham lam ở làng bên. Ông anh nghe xong thì lập tức bỏ hết mọi việc dang dở, chạy thẳng đến nhà em ép phải kể rõ đầu đuôi câu chuyện. Em trai hiền lành thật thà nên khai sạch không giấu giếm chuyện gì cả. Mắt ông anh sáng quắc lên vì tham, lập tức nghĩ ra cú scam đỉnh cao: đổi toàn bộ gia tài lấy cây khế cằn cỗi của em, drama gia đình bắt đầu từ đây.",
        # Scene 11 — Body 9: anh chờ chim + ICONIC lại (slang: cười xỉu, hành gà)
        "Em trai hiền lành đồng ý đổi tài sản ngay, không nghi ngờ một chút ý đồ xấu nào của ông anh. Ông anh vội dọn về túp lều cũ cạnh cây khế, ngồi chờ chim phượng hoàng với tâm thế háo hức bồn chồn. Đúng mùa khế chín, chim quả nhiên bay đến như mọi lần trước. Ông anh nhảy ra giả vờ than vãn y hệt em trai nhưng giọng điệu giả tạo lộ liễu, cười xỉu vì hành gà quá lộ. Chim vẫn phán câu cũ rõ ràng: ăn một quả trả một cục vàng, may túi ba gang mang theo mà đựng.",
        # Scene 12 — Body 10: anh may túi 9 gang (slang: đại boss, lú)
        "Ông anh gật đầu lia lịa nhưng trong đầu đã nảy số toán cộng trừ nhân chia. Thay vì túi ba gang khiêm tốn như em, ông may luôn cái túi chín gang khổng lồ, đắc ý trong lòng đại boss giàu nhất vùng. Sáng hôm sau chim chở ông ra đảo vàng. Đến nơi, ông lú không biết tiết chế, nhồi vàng vào túi đến mức miệng túi không khép lại nổi, còn cố nhét đầy túi áo túi quần đến mức người căng phồng cứng đơ.",
        # Scene 13 — Body 11: anh rơi biển (slang: đăng xuất, GG)
        "Đường về quê hương biến thành một thảm họa thực sự vì cái túi vàng quá nặng. Chim đập cánh giữa biển khơi mà ngày càng đuối sức, bay xuống thấp dần thấp dần theo từng nhịp. Đến giữa biển sâu, chim đành nghiêng cánh hất văng ông anh cùng túi vàng rơi xuống nước. Ông anh vẫn cố ôm chặt túi vàng không chịu buông tay, mặc cho sóng đánh ầm ầm xung quanh. Cuối cùng trọng lượng vàng kéo ông chìm xuống đáy biển sâu thẳm, đăng xuất khỏi câu chuyện không một ai cứu được, GG cho lòng tham không đáy.",
        # Scene 14 — Moral (slang: dân chơi, đại boss)
        "Câu chuyện khép lại với một bài học cực kỳ thấm thía về lòng tham trong cuộc đời này. Sống trên đời phải biết thế nào là đủ, vì người không biết đủ thì có bao nhiêu cũng không thấy thỏa mãn. Người em khiêm tốn chỉ lấy đúng những gì cần, được sống bình yên hạnh phúc đến cuối đời bên dân làng yêu quý. Còn người anh, vì muốn lấy nhiều hơn phần của mình, cuối cùng phải trả giá bằng cả mạng sống bản thân. Tham thì thâm, đó là quy luật ngàn đời mà các đại boss giàu có lẫn dân chơi bình thường đều phải khắc cốt ghi tâm.",
    ],
    "image_prompts": [
        # 1 — Hook atmospheric
        f"Atmospheric establishing shot: ancient Vietnamese rural village at dusk, single khế tree silhouette in foreground, thatched houses, mist, no characters, mood-setting cinematic.",
        # 2 — Hook movie poster
        f"Movie-poster composition: {EM_TRAI} on LEFT half humble with bamboo basket, large khế tree with golden fruits in center, {ANH_TRAI} on RIGHT half smug with gold chains, dramatic split lighting.",
        # 3 — Body 1: chia tài sản + movie mapping
        f"Inheritance division scene: {ANH_TRAI} smug greedily holding deeds/papers and gold coins surrounded by livestock, {EM_TRAI} humble pointing at single khế tree and small thatched hut, contrast composition.",
        # 4 — Body 2: em chăm khế
        f"Rural scene: {EM_TRAI} watering a young khế tree with bamboo bucket, golden khế fruits hanging from branches, village children playing nearby happy with khế fruits in hands, peaceful warm morning.",
        # 5 — Body 3: chim đến ăn khế
        f"Magical moment: {CHIM_PHUONG} perched majestically on khế tree branch eating golden fruits, glowing rainbow feathers, {EM_TRAI} watching from doorway of hut in awe, soft mystical light.",
        # 6 — Body 4: em than chim
        f"Dialogue scene: {EM_TRAI} kneeling humbly under khế tree pleading with hands clasped, {CHIM_PHUONG} on branch looking down kindly with intelligent glowing eyes, sun rays through leaves.",
        # 7 — Body 5: chim đáp iconic phrase
        f"Mystical talking bird scene: {CHIM_PHUONG} speaking with mouth open beak, magical golden sparkles around words floating in air representing speech, {EM_TRAI} eyes wide in surprise, dramatic close-up framing, golden glow.",
        # 8 — Body 6: em đi đảo vàng
        f"Mystical flying scene: {EM_TRAI} riding on back of {CHIM_PHUONG} flying over ocean toward a sparkling golden island in distance, dawn light, small {TUI_BA_GANG} clutched in hand, mystical sparkles trailing.",
        # 9 — Body 7: em giúp dân làng
        f"Generous scene: {EM_TRAI} dressed simply distributing rice and money to poor villagers from new wooden house, happy children smiling around khế tree heavy with fruits, sunny day, generous mood.",
        # 10 — Body 8: anh tham đến đổi tài sản
        f"Greedy negotiation scene: {ANH_TRAI} aggressively shaking hand with {EM_TRAI}, exchanging gold coins for ownership of khế tree, paper contracts, calculating greedy expression vs honest humble.",
        # 11 — Body 9: anh chờ chim + iconic phrase repeat
        f"Same talking bird scene returning: {CHIM_PHUONG} on khế tree speaking same line with golden sparkles, {ANH_TRAI} listening with greedy calculating eyes, smirk forming, contrast to {EM_TRAI}'s innocent reaction earlier.",
        # 12 — Body 10: anh may túi 9 gang + nhồi vàng
        f"Greedy preparation scene: {ANH_TRAI} sitting in hut frantically sewing an oversized {TUI_CHIN_GANG} with thread and needle, gold coins overflowing nearby, calculating greedy face, comedic exaggerated size.",
        # 13 — Body 11: anh rơi xuống biển + chết
        f"Tragic ocean scene: {CHIM_PHUONG} flying mid-air over stormy ocean tilting wings struggling, {ANH_TRAI} with enormous golden treasure bag sliding off bird falling into dark waves below, dramatic doom.",
        # 14 — Moral peaceful
        f"Peaceful resolution: {EM_TRAI} sitting under flourishing khế tree at sunset, helping village children, warm amber palette, contemplative oil-painting feel, hopeful gentle mood.",
    ],
    "motions": ["static","zoom_in","static","static","static","static","static","static","static","static","static","static","static","static","zoom_out"],
    "caption_hook": "Anh em đã nghe Ăn Khế Trả Vàng kiểu phim Wolf of Wall Street chưa? 💰 Tham thì thâm — đại boss của câu chuyện greed!",
    "caption_bullets": [
        "Anh tham chiếm hết tài sản, em chỉ được cây khế",
        "Chim phượng hoàng đến ăn khế",
        "Ăn một quả trả một cục vàng, may túi ba gang",
        "Em hiền lành lấy vừa đủ, sống sung túc khiêm tốn",
        "Anh tham đổi tài sản lấy cây khế",
        "Anh may túi chín gang nhồi vàng đầy ụ",
        "Chim chở quá nặng, anh rơi xuống biển chết oan"
    ],
    "caption_moral": "Câu chuyện dạy ta biết đủ là hạnh phúc, tham thì thâm — lòng tham không kiềm chế sẽ tự hủy diệt mình."
}

# ================ BOOK 5: SƠN TINH THỦY TINH (REDO with detailed prose + intro) ================
SON_TINH = _char("Sơn Tinh mountain lord", "young Vietnamese man: moss-green solid hoodie no print + ripped black jeans, white Air Force sneakers, large gold chain, undercut blonde hair, natural confident stance NOT gym flex")
THUY_TINH = _char("Thủy Tinh sea lord", "young Vietnamese man: aqua-blue bomber jacket solid + black streetwear shorts, white slide sandals, aviator sunglasses, platinum blonde hair, water aura around feet")
VUA_HUNG = _char("Vua Hùng Vương đời 18", "elderly Vietnamese king: red royal robe with aviator sunglasses and Apple Watch, long white beard, golden throne")
MI_NUONG = _char("Princess Mị Nương", "young Vietnamese princess: cream pastel áo dài with white Air Force sneakers underneath, long black hair, gold hair pin, gentle elegant smile")
COURT = "ancient Văn Lang royal palace interior: red lacquered wooden columns, hanging red oil lanterns, jade floor tiles, traditional NPCs in áo tứ thân blurred background"

SON_TINH_BOOK = {
    "slug": "son-tinh-thuy-tinh",
    "title": "Sơn Tinh Thủy Tinh",
    "story_summary": "Văn Vở Gen Z. Sơn Tinh và Thủy Tinh tranh giành Mị Nương — đại chiến núi vs nước. Phiên bản kiểu phim Crazy Rich Asians (2018).",
    "scripts": [
        # Scene 1 — Hook short
        "Trong kho tàng truyền thuyết Việt Nam, có một câu chuyện về cuộc tranh giành tình yêu giữa 2 vị thần khét. Phiên bản chi tiết của truyện Sơn Tinh Thủy Tinh, anh em ngồi vững nha vì combat núi vs nước siêu epic.",
        # Scene 2 — Hook short plot tease
        "Câu chuyện có Vua Hùng kén rể cho Mị Nương, có 2 chàng trai siêu bá tranh nhau. Có sính lễ oái oăm, có đại chiến dâng núi nuốt nước, có giải thích vì sao Bắc Bộ năm nào cũng lụt.",
        # Scene 3 — Body 1: Vua Hùng + Mị Nương + movie mapping
        "Ngày xửa ngày xưa, vào đời vua Hùng Vương thứ mười tám, vua có một cô con gái duy nhất tên là Mị Nương. Cô công chúa lúc bấy giờ đẹp nghiêng nước nghiêng thành, tính tình lại dịu dàng đoan trang nức tiếng khắp Văn Lang. Vua Hùng cưng con như báu vật, muốn tìm cho con một chàng rể thật xứng đáng. Vua ra chiếu rộng cả nước, ai có tài năng và đức độ đều có thể đến cầu hôn công chúa.",
        # Scene 4 — Body 2: 2 ứng viên xuất hiện
        "Một ngày đẹp trời, bỗng nhiên có hai boi phố chính hiệu cùng đến cầu hôn một lúc khiến cả triều ngỡ ngàng. Một người tên Sơn Tinh, chúa tể vùng núi Tản Viên cao ngất, có phép thuật dời non lấp biển. Người kia tên Thủy Tinh, chúa tể biển khơi mênh mông, có phép hô mưa gọi gió dâng nước. Cả hai đều tài giỏi không ai kém ai, cả hai đều siêu bá đến mức Vua Hùng không thể chọn được người nào.",
        # Scene 5 — Body 3: Vua Hùng phán sính lễ iconic (FULL list)
        "Vua Hùng lúng túng vô cùng vì cả hai đều xứng đáng làm phò mã, không biết phải chọn người nào không phật ý kia. Bí bách quá Vua nghĩ ra một cách scam khá hài hước, phán điều kiện sính lễ kỳ quặc. Vua bảo: ai sáng mai mang đủ một trăm ván cơm nếp, hai trăm nệp bánh chưng, voi chín ngà, gà chín cựa, ngựa chín hồng mao đến trước, ta sẽ gả công chúa cho. Hai chàng trai gật đầu nhận lời, lập tức trở về quê chuẩn bị sính lễ ngay trong đêm khuya.",
        # Scene 6 — Body 4: Sơn Tinh chuẩn bị + đến trước cưới
        "Sơn Tinh là đại boss vùng núi nên có sẵn nhiều thú lạ và lương thực trong rừng sâu, chuẩn bị sính lễ rất nhanh chóng. Anh sai thuộc hạ đi khắp các đỉnh núi cao, mang về đầy đủ một trăm ván cơm nếp, hai trăm nệp bánh chưng, voi chín ngà, gà chín cựa, ngựa chín hồng mao đủ ba con. Sáng sớm tinh mơ Sơn Tinh đã dẫn đoàn sính lễ kỳ thú đến cung vua trước rồi. Vua Hùng theo lời hứa giữ chữ tín, ngay lập tức gả công chúa Mị Nương cho Sơn Tinh và rước cô về núi Tản Viên.",
        # Scene 7 — Body 5: Thủy Tinh tới muộn + sang chấn
        "Thủy Tinh ở dưới biển sâu phải vất vả lắm mới tìm được đủ sính lễ kỳ quặc theo yêu cầu. Khi tới cung vua thì đã muộn vài giờ, công chúa Mị Nương đã được Sơn Tinh rước về núi rồi. Thủy Tinh đứng giữa cung điện trống không, tâm lý vỡ vụn sang chấn nặng nề không nói được câu nào. Hận tới tận xương tủy, Thủy Tinh thề sẽ trả thù Sơn Tinh và cướp lại Mị Nương bằng mọi giá.",
        # Scene 8 — Body 6: Thủy Tinh combat start
        "Thủy Tinh trở về biển lập tức hô mưa gọi gió, dâng nước cuồn cuộn đuổi theo Sơn Tinh tận núi Tản Viên. Combo bão tố sóng thần liên hoàn cực gắt, nước dâng cao chìm cả đồng bằng Bắc Bộ. Nhà cửa làng mạc đều bị nhấn chìm, gia súc trôi nổi khắp nơi trong biển nước mênh mông. Dân chúng kêu cứu khắp nơi, ai cũng nghĩ đây là ngày tận thế của loài người sắp đến rồi.",
        # Scene 9 — Body 7: Sơn Tinh counter
        "Sơn Tinh từ trên đỉnh núi Tản Viên bình tĩnh nhìn cảnh nước dâng, không hề hoảng sợ. Anh dâng phép thần lập tức nâng núi cao thêm chống lại nước, đắp đê đập chặn dòng nước cuồn cuộn. Nước Thủy Tinh dâng tới đâu, núi Sơn Tinh cao tới đó, hai bên combat ngang ngửa không ai chịu thua. Cuộc chiến giữa núi và nước kéo dài cả nhiều ngày đêm, trời đất rung chuyển thiên tai khắp nơi.",
        # Scene 10 — Body 8: continuing clash
        "Càng đánh càng quyết liệt, Thủy Tinh dùng đủ mọi cách dâng nước cao hơn nhưng Sơn Tinh vẫn dâng núi cao hơn nữa. Hai bên thi nhau trổ tài, không bên nào chịu lùi một bước trước đối thủ. Sấm chớp nổ vang trời, sóng thần đánh vỗ vào các đỉnh núi vang dội như muốn xé toang vũ trụ. Cảnh tượng combat thần thoại chưa từng có trong lịch sử Việt Nam, đỉnh cao của các trận đại chiến thần thánh.",
        # Scene 11 — Body 9: Thủy Tinh thua rút quân
        "Đánh mãi không thắng được Sơn Tinh, cuối cùng Thủy Tinh đành chịu thua rút quân về biển trong tủi nhục. Nhưng hận thù trong lòng chưa nguôi được, Thủy Tinh thề từ nay năm nào cũng sẽ trở lại để combat thêm. Cứ đến mùa mưa lũ tháng bảy tháng tám hằng năm, Thủy Tinh lại dâng nước tấn công Sơn Tinh. Đây là lý do dân tộc Việt Nam mỗi năm đều phải đối mặt với lũ lụt ở vùng đồng bằng Bắc Bộ.",
        # Scene 12 — Body 10: Sơn Tinh + Mị Nương hạnh phúc
        "Sơn Tinh và công chúa Mị Nương từ đó sống hạnh phúc trên đỉnh núi Tản Viên cao đến tận mây. Hai vợ chồng sinh con đẻ cái, sống cuộc đời bình yên giữa núi rừng xanh ngát quanh năm. Thủy Tinh dù mỗi năm trở lại tấn công, nhưng chưa bao giờ thắng được Sơn Tinh kiên trì kiên định. Đại boss thực sự không phải kẻ mạnh nhất, mà là người biết chấp nhận và bảo vệ những gì mình yêu thương.",
        # Scene 13 — Body 11: giải thích lũ lụt + dân Việt thích nghi
        "Truyền thuyết này giải thích vì sao mỗi năm cứ đến mùa mưa, miền Bắc Việt Nam lại có lũ lụt lớn. Đó là Thủy Tinh đang trả thù Sơn Tinh, dâng nước lên cố cướp lại Mị Nương từ tay tình địch. Dân tộc Việt Nam từ xưa đã học cách thích nghi với lũ lụt, xây đê đắp đập chống chọi y như Sơn Tinh. Câu chuyện trở thành biểu tượng văn hóa sâu sắc về sức mạnh thiên nhiên và lòng kiên cường của con người.",
        # Scene 14 — Moral
        "Câu chuyện Sơn Tinh Thủy Tinh dạy ta rằng trong tình yêu phải biết chấp nhận, không thể ép buộc người khác yêu mình. Đối thủ giỏi hơn thì hãy nâng cấp bản thân để xứng đáng, không phải dùng bạo lực phá hủy thế giới xung quanh. Sự kiên trì bảo vệ những gì mình yêu thương luôn là sức mạnh lớn nhất trong cuộc đời. Đây là truyền thuyết giải thích hiện tượng lũ lụt nhưng cũng là bài học sâu sắc về tình yêu và sự trưởng thành.",
    ],
    "image_prompts": [
        # 1 — Hook atmospheric
        f"Atmospheric establishing shot: ancient Văn Lang village skyline at dawn, mist rising from rice paddies, distant pagoda silhouettes, mountains in background, no characters visible, mood-setting cinematic.",
        # 2 — Hook movie poster
        f"Movie-poster composition: {SON_TINH} on LEFT half with mountains behind, {THUY_TINH} on RIGHT half with ocean spray, split-screen dramatic lighting, fairy-tale poster framing.",
        # 3 — Body 1: Vua Hùng + Mị Nương intro
        f"Royal court scene: {VUA_HUNG} on golden throne, {MI_NUONG} standing beside him gracefully. {COURT}. Cinematic two-shot composition warm palette.",
        # 4 — Body 2: 2 ứng viên xuất hiện
        f"Royal court entrance: {SON_TINH} and {THUY_TINH} both entering simultaneously, low-angle hero shot, {COURT}, dramatic spotlight on both characters.",
        # 5 — Body 3: sính lễ iconic (full list)
        f"{VUA_HUNG} pointing dramatically forward, magical golden hologram floating above showing FULL items: 100 trays of glutinous rice cơm nếp, 200 stacks of bánh chưng square cakes, white nine-tusk elephant, golden nine-spur rooster, red nine-mane horse. {COURT}.",
        # 6 — Body 4: Sơn Tinh victorious procession
        f"Victorious procession: {SON_TINH} leading magical procession of white nine-tusk elephant, golden rooster, red horse, plus stacks of bánh chưng and cơm nếp trays, into the royal court at sunrise, golden warm lighting, victory aura.",
        # 7 — Body 5: Thủy Tinh tới muộn
        f"{THUY_TINH} standing alone in empty royal court, looking around in shock and devastation, dramatic close-up of heartbroken face, deep blue + red neon ambient, empty {COURT}.",
        # 8 — Body 6: Thủy Tinh combat start (tidal wave)
        f"{THUY_TINH} standing on coastal cliff, both arms raised toward dark stormy sky, massive 30-meter tidal wave forming behind, lightning bolts crackling, dynamic action pose.",
        # 9 — Body 7: Sơn Tinh counter (mountains rising)
        f"Split-screen showdown: LEFT {SON_TINH} stomping ground causing massive mountain peaks to rise, RIGHT {THUY_TINH} sending tidal waves crashing, center clash of mountain vs water elements, epic.",
        # 10 — Body 8: continuing clash apocalyptic
        f"Continuing epic clash: even taller mountains rising vs even larger ocean waves crashing, lightning + thunder + storm, two opposing forces of nature collision, apocalyptic dramatic landscape.",
        # 11 — Body 9: Thủy Tinh thua + underwater dejected
        f"{THUY_TINH} sitting cross-legged dejected at bottom of ocean floor surrounded by jellyfish, glowing calendar hologram beside him with months 7 and 8 highlighted in red (flood season), moody deep blue.",
        # 12 — Body 10: Sơn Tinh + Mị Nương sống hạnh phúc
        f"Peaceful happy scene: {SON_TINH} and {MI_NUONG} standing together on top of Tản Viên mountain holding hands at golden sunset, looking down at peaceful valley below with rice paddies, children playing nearby, warm amber palette joyful.",
        # 13 — Body 11: lũ lụt Bắc Bộ + dân Việt thích nghi
        f"Modern-historical scene: Vietnamese villagers building earthen dam đê đập along river to hold back floodwaters, ancient costume workers with shovels and baskets, dark stormy sky above with hint of {THUY_TINH}'s face in clouds, perseverance mood.",
        # 14 — Moral closing
        f"Closing peaceful sunset over Vietnamese mountain landscape: rice paddies, rivers, mountains, warm amber golden palette, less neon more contemplative oil-painting feel, hopeful mood.",
    ],
    "motions": ["static","zoom_in","static","static","static","static","static","static","static","static","static","static","static","static","zoom_out"],
    "caption_hook": "Anh em nghe Sơn Tinh Thủy Tinh kiểu phim Crazy Rich Asians chưa? ⛰️🌊 Combat dâng núi nuốt nước siêu epic!",
    "caption_bullets": [
        "Vua Hùng kén rể cho Mị Nương",
        "Sơn Tinh + Thủy Tinh cùng cầu hôn",
        "Sính lễ voi chín ngà gà chín cựa ngựa chín hồng mao",
        "Sơn Tinh đến trước cưới Mị Nương",
        "Thủy Tinh sang chấn dâng nước trả thù",
        "Combat núi vs nước ngang ngửa",
        "Hằng năm Thủy Tinh quay lại — giải thích lũ lụt Bắc Bộ"
    ],
    "caption_moral": "Câu chuyện dạy ta trong tình yêu phải biết chấp nhận, đối thủ giỏi hơn thì hãy nâng cấp bản thân."
}

# ================ BOOK 6: TẤM CÁM ================
TAM = _char("Tấm", "young Vietnamese woman, kind orphan: cream pastel áo dài with white Air Force sneakers, long black hair tied simple, no makeup natural beauty, gentle modest pose")
CAM_TC = _char("Cám stepsister", "young Vietnamese woman, spoiled: trendy pastel pink oversized hoodie SOLID no print, ripped jeans, white sneakers, long black hair with red streaks, smirking arrogant pose")
DI_GHE_TC = _char("dì ghẻ stepmother", "middle-aged Vietnamese woman, cruel: dark purple blazer SOLID over áo nâu sòng, blood-red lipstick, hair tight bun, scolding angry pose hands on hips")
BUT_TC = _char("Bụt deity", "kind elderly Buddhist deity: white flowing robe with neon cyan glow aura, long silver beard, holding wooden staff, soft golden halo")
VUA_TC = _char("Vietnamese king", "handsome young king: red royal robe with gold trim, modern aviator sunglasses + gold chain underneath, undercut hair, dignified yet trendy")
BA_LAO = _char("bà lão old woman", "elderly Vietnamese grandmother: simple brown áo bà ba, gray hair bun, wrinkled kind face")

TAM_CAM_BOOK = {
    "slug": "tam-cam",
    "title": "Tấm Cám",
    "story_summary": "Văn Vở Gen Z. Tấm mồ côi bị dì ghẻ + Cám hành hạ, được Bụt giúp, lên cung làm hoàng hậu rồi bị giết, hóa kiếp nhiều lần trả thù. Phiên bản kiểu phim Cinderella (Disney 2015).",
    "scripts": [
        # Scene 1 — Hook short
        "Trong kho tàng cổ tích Việt Nam, có một câu chuyện về cuộc trả thù tàn khốc nhất sau khi bị mưu hại. Phiên bản chi tiết của truyện Tấm Cám, anh em ngồi vững nha vì câu chuyện này có nhiều tình tiết bất ngờ rất khó tin.",
        # Scene 2 — Hook short plot tease
        "Câu chuyện có dì ghẻ ác độc, có Bụt từ bi giúp đỡ, có cá bống huyền thoại, có bầy chim sẻ kỳ diệu. Có hóa kiếp 4 lần để trả thù, có drama kết cục tàn khốc nhất trong cổ tích Việt.",
        # Scene 3 — Body 1: Tấm mồ côi + movie mapping
        "Ngày xửa ngày xưa, có cô gái tên là Tấm mồ côi mẹ từ khi còn nhỏ, sống cùng dì ghẻ và em gái Cám. Cha Tấm tục huyền lấy người dì có sẵn con riêng, không lâu sau cha cũng qua đời để lại Tấm tội nghiệp. Cuộc đời Tấm từ đó siêu phèn, sáng dậy sớm quét nhà, chiều giặt giũ nấu ăn không một phút nghỉ.",
        # Scene 4 — Body 2: Bắt tép challenge
        "Một hôm dì ghẻ đưa hai chị em mỗi người một cái giỏ, bảo ra đồng bắt tép suốt cả buổi sáng. Bà ta hứa nếu ai bắt được đầy giỏ trước, sẽ được thưởng một cái yếm đỏ thắm xinh xắn. Tấm cắm cúi xuống ruộng cẩn thận xúc từng con tép một, còn Cám thì lười biếng nằm chơi trên bờ chẳng làm gì cả.",
        # Scene 5 — Body 3: Cám scam + iconic dialogue
        "Đến trưa, giỏ Tấm đã gần đầy còn giỏ Cám vẫn trống không. Lúc đó Cám nghĩ ra một kế bẩn, gọi với sang: chị ơi chị, đầu chị lấm chị hụp cho sâu, kẻo về dì mắng. Tấm thật thà nghe lời, cởi áo xuống sông tắm gội đầu cẩn thận. Trong lúc Tấm đang gội, Cám lén trút hết tép trong giỏ Tấm sang giỏ mình rồi ung dung mang về nhận yếm đỏ.",
        # Scene 6 — Body 4: Bụt hiện cho cá bống
        "Tấm tắm xong lên bờ, thấy giỏ trống không thì òa khóc nức nở giữa đồng. Bỗng nhiên một ông lão râu tóc bạc phơ hiện ra giữa làn sương sáng, ấy chính là Bụt. Bụt hỏi vì sao khóc rồi an ủi, bảo Tấm nhìn vào giỏ xem còn lại gì không. Trong giỏ chỉ còn một con cá bống bé tí, Bụt dặn Tấm đem về thả vào giếng nuôi, mỗi ngày cho ăn cơm và gọi nó lên.",
        # Scene 7 — Body 5: ICONIC gọi cá bống "bống bống bang bang lên ăn cơm vàng cơm bạc nhà ta"
        "Từ đó mỗi ngày Tấm mang cơm ra giếng, đứng bên thành giếng cất tiếng gọi cá bống. Tấm hát: bống bống bang bang, lên ăn cơm vàng cơm bạc nhà ta, chớ ăn cơm hẩm cháo hoa nhà người. Cá bống quen thân hễ nghe tiếng là ngoi lên đớp mồi ngay lập tức. Tấm coi cá bống như người bạn duy nhất, ngày nào cũng tâm sự chia sẻ tâm tư mọi nỗi buồn vui trong cuộc sống cay đắng.",
        # Scene 8 — Body 6: mẹ con Cám rình giả giọng giết cá bống
        "Mẹ con Cám thấy Tấm hằng ngày mang cơm ra giếng thì sinh nghi ngờ, lén rình theo dõi xem chuyện gì. Họ nghe Tấm hát câu thần chú gọi cá bống, lập tức nảy ra ý đồ độc ác để hại em. Hôm sau khi Tấm đi vắng, mẹ con Cám ra giếng giả giọng Tấm gọi: bống bống bang bang lên ăn cơm vàng cơm bạc nhà ta. Cá bống ngoi lên không nghi ngờ, lập tức bị họ bắt mang về làm thịt ăn no nê.",
        # Scene 9 — Body 7: Bụt cho xương cá chôn 4 chân giường
        "Tấm về tới giếng gọi mãi cá bống không thấy lên, sợ hãi tìm khắp thì thấy chỉ còn cục máu nổi lên mặt nước. Tấm hiểu ra cá bống đã bị giết, ngồi bên giếng khóc thảm thiết cả đêm không nín. Bụt lại hiện ra an ủi, bảo Tấm đi tìm xương cá bống về chôn dưới bốn chân giường. Bụt dặn rằng đến mùa hội năm sau, những xương này sẽ giúp Tấm có một bất ngờ thật lớn.",
        # Scene 10 — Body 8: dì ghẻ trộn cám gạo bắt nhặt
        "Mùa xuân năm ấy đến, nhà vua mở hội lớn kén vợ cho hoàng tử, cả nước nô nức đi xem. Mẹ con Cám diện đẹp lên đường còn Tấm cũng xin theo, nhưng dì ghẻ không cho. Dì ghẻ trộn một thúng cám với một thúng gạo, bắt Tấm phải nhặt riêng từng hạt mới được đi hội. Tấm ngồi cả buổi sáng không nhặt nổi vì số lượng quá khổng lồ, bật khóc tủi thân vô cùng.",
        # Scene 11 — Body 9: ICONIC bầy chim sẻ giúp lựa đậu
        "Bụt lại hiện ra an ủi, bảo Tấm đừng khóc rồi sai một bầy chim sẻ từ trên trời bay xuống giúp. Bầy chim sẻ hàng trăm con sà xuống chiếc nia, mỗi con một hạt nhặt cám và gạo ra hai phần riêng biệt cực kỳ nhanh chóng. Chỉ trong giây lát mọi việc đã xong xuôi gọn gàng, cám một bên gạo một bên không hề lẫn lộn. Tấm cảm tạ Bụt và bầy chim sẻ rồi vội vàng chuẩn bị quần áo đi hội.",
        # Scene 12 — Body 10: xương cá → quần áo + đi hội + đánh rơi giày
        "Tấm nhớ lời Bụt dặn đào bốn chân giường lên, quả nhiên xương cá bống đã biến thành quần áo lộng lẫy và đôi giày thêu xinh đẹp. Tấm thay đồ vào trở nên xinh đẹp tuyệt trần, vui mừng chạy đi hội cho kịp giờ. Khi qua một chiếc cầu, không may cô đánh rơi một chiếc giày xuống sông trong vội vã. Vua đi ngang qua nhặt được liền truyền lệnh khắp nước ai đi vừa chiếc giày này sẽ cưới làm hoàng hậu.",
        # Scene 13 — Body 11: cả nước thi giày + Tấm thắng
        "Cả nước đổ xô đến thử giày để có cơ hội lên làm hoàng hậu trong cung. Các bậc tiểu thư đẹp đẽ nhất xếp hàng dài cũng không ai đi lọt được vào chiếc giày kỳ lạ. Đến lượt Tấm, dù mặc áo nâu sòng nghèo nàn nhưng chân vừa khít chiếc giày như đo đúc sẵn. Vua mừng rỡ truyền rước cô về cung làm hoàng hậu giữa sự ngỡ ngàng cay cú của mẹ con dì ghẻ.",
        # Scene 14 — Body 12: Tấm về giỗ + bị chặt cau chết
        "Một thời gian sau đến ngày giỗ cha, Tấm xin phép Vua về nhà cúng cho có hiếu. Dì ghẻ giả vờ ân cần đón tiếp, bảo Tấm trèo lên cây cau hái quả thật tươi xuống cúng cha. Tấm thật thà leo lên đến tận ngọn cây thì dì ghẻ ở dưới đem rìu chặt đứt gốc tàn nhẫn. Cây cau đổ rầm xuống ao, Tấm rơi xuống chết ngay tại chỗ một cách oan ức tức tưởi.",
        # Scene 15 — Body 13: hóa kiếp 4 lần
        "Tấm chết oan ức nên hồn không siêu thoát được, hóa thành chim vàng anh hót líu lo bay vào cung. Cám ghen tị bắt giết chim, lông chim rơi xuống mọc thành cây xoan, sau biến thành khung cửi dệt vải. Cám đốt khung cửi luôn cho yên chuyện, tro tàn bay đi mọc thành cây thị, ra một quả thị thơm lừng cả vùng. Một bà lão đi qua nhặt thị về để trong nhà, thị nứt ra lộ một cô gái xinh đẹp chính là Tấm hóa thân.",
        # Scene 16 — Body 14: Vua nhận lại Tấm + Cám đăng xuất
        "Tấm sống với bà lão, một hôm Vua đi ngang qua ghé vào uống nước, nhận ra trầu cánh phượng giống của Tấm têm ngày xưa. Hai vợ chồng đoàn tụ trong nước mắt, Tấm cùng Vua trở về cung sau bao biến cố. Cám thấy Tấm trở lại còn đẹp hơn xưa thì kinh hoàng hỏi: chị ơi sao chị đẹp thế làm thế nào em làm theo với. Tấm bảo Cám muốn đẹp thì xuống hố tắm nước sôi cho da trắng mịn, Cám ngu ngốc làm theo và chết tại chỗ. Tấm sai làm mắm thịt Cám gửi cho dì ghẻ ăn, dì ghẻ biết sự thật thì lăn ra chết tức tưởi.",
        # Scene 17 — Body 15: Moral
        "Câu chuyện Tấm Cám tuy đen tối nhưng dạy cho chúng ta nhiều bài học sâu sắc về cuộc đời này. Cái thiện cuối cùng sẽ chiến thắng cái ác, nhưng không phải dễ dàng mà phải trải qua nhiều thử thách đau đớn. Sự kiên trì không bỏ cuộc và lòng bao dung của người tốt sẽ luôn được đền đáp xứng đáng. Nhưng đồng thời, ác giả ác báo cũng là một quy luật không một ai thoát được trong vũ trụ rộng lớn này.",
    ],
    "image_prompts": [
        # 1 — Hook atmospheric
        f"Atmospheric establishing shot: ancient Vietnamese rural village at twilight, mist rising from rice paddies, single banyan tree silhouette, no characters, mood-setting cinematic.",
        # 2 — Hook movie poster
        f"Movie-poster composition: {TAM} on LEFT half humble with broom, {CAM_TC} on RIGHT half smug with arms crossed, a glowing magical slipper floating between them, dramatic split-screen lighting, fairy-tale poster framing.",
        # 3 — Body 1: Tấm mồ côi + dì ghẻ
        f"Rural scene: {TAM} sweeping a dusty courtyard alone at dawn looking exhausted but determined, {DI_GHE_TC} watching coldly with arms crossed in shadow behind, melancholy lighting with single shaft of sunlight on Tấm, thatched roof village background.",
        # 4 — Body 2: Bắt tép
        f"Wide shot at rural river: {TAM} on LEFT diligently scooping shrimp into bamboo basket with serious focus, {CAM_TC} on RIGHT lazily lounging on rock with empty basket, clear morning sunlight, reeds, rice paddies behind.",
        # 5 — Body 3: Cám scam + dialogue
        f"{CAM_TC} sneaking away from riverbank with two full bamboo baskets of shrimp, sly satisfied smirk looking back over shoulder, blurred in distant background {TAM} bathing in river unaware, dramatic dappled light through trees.",
        # 6 — Body 4: Bụt hiện cho cá bống
        f"Mystical scene by small village well: {TAM} kneeling crying, {BUT_TC} emerging from glowing cyan mist holding small fish in palm, beam of golden light from sky, rural Vietnamese village background, magical realism mood.",
        # 7 — Body 5 ICONIC gọi cá bống ("bống bống bang bang...")
        f"Iconic moment: {TAM} standing beside a stone village well singing with mouth open, a small black-spotted fish cá bống emerging from water surface looking up at her, magical golden musical notes floating in air around Tấm's mouth representing her singing, soft mystical warm light, intimate emotional moment.",
        # 8 — Body 6: mẹ con Cám rình giả giọng giết bống
        f"Sneaky dark scene: {CAM_TC} and {DI_GHE_TC} hiding behind bushes by the well at dusk, {CAM_TC} cupping hands to mouth singing fake voice, the cá bống fish emerging unsuspecting from water, sinister mood with cold blue ambient light.",
        # 9 — Body 7: Bụt cho xương chôn 4 chân giường
        f"{TAM} kneeling crying by well now empty, blood drops floating on water surface visible, {BUT_TC} appearing again with kindly expression pointing toward old wooden bed in hut, mystical golden glow, sad but hopeful mood.",
        # 10 — Body 8: dì ghẻ trộn cám gạo bắt nhặt
        f"{DI_GHE_TC} pouring large basket of rice mixed with bran onto wide woven flat tray nia in dirt courtyard, {TAM} kneeling beside in despair with tears, {DI_GHE_TC} pointing finger sternly with mean expression, mocking servants in background.",
        # 11 — Body 9 ICONIC bầy chim sẻ giúp lựa đậu
        f"Iconic magical scene: dozens of small Vietnamese sparrow birds chim sẻ flying down from sky in formation, landing on a wide flat woven tray nia full of mixed grains, each bird picking up grains and separating them into two distinct piles, {TAM} watching in awe with grateful tears, {BUT_TC} standing with magical glow nearby, sunlight beams through trees, golden mystical mood.",
        # 12 — Body 10: xương → quần áo + đi hội + đánh rơi giày
        f"Dynamic action shot: {TAM} now wearing beautiful cream golden áo dài with white sneakers running across wooden bridge over river, one elegant slipper falling mid-air into water below, festival lanterns and crowds visible blurred behind, dramatic motion blur, magical transformation sparkles trailing.",
        # 13 — Body 11: Vua rước Tấm về cung
        f"Royal wedding scene: {VUA_TC} placing the white slipper on {TAM}'s foot, both kneeling on red carpet, ancient Vietnamese royal palace interior with red lacquered columns and lanterns, warm golden lighting, romantic but stylish vibe.",
        # 14 — Body 12: Tấm chặt cau chết
        f"Tragic scene: a tall thin areca cau tree, {TAM} clinging halfway up looking down in horror, at base {DI_GHE_TC} swinging an axe mid-strike, cau tree starting to topple over small pond visible at base, dramatic high-contrast lighting, dark mood.",
        # 15 — Body 13: hóa kiếp 4 transformations
        f"Magical montage with golden swirling particles: a beautiful yellow vàng anh bird perched on royal window dissolving into a wooden weaving loom khung cửi, dissolving into a green star apple cây thị tree with one large fragrant fruit hanging, ancient palace blurred behind, mystical cyan and gold light.",
        # 16 — Body 14: Tấm trở lại + Cám đăng xuất
        f"Final confrontation scene: {TAM} fully restored standing tall by throne with cold determined expression, {VUA_TC} standing protectively beside her, {CAM_TC} and {DI_GHE_TC} kneeling on floor terrified, dark dramatic red lighting, ominous royal palace interior.",
        # 17 — Moral
        f"Peaceful resolution: {TAM} and {VUA_TC} standing together overlooking peaceful Vietnamese village at sunset from a hilltop, warm amber palette, contemplative oil-painting feel, hopeful uplifting mood.",
    ],
    "motions": ["static"] * 18,  # 1 intro + 17 narrators = 18 motions
    "caption_hook": "Anh em đã nghe Tấm Cám kiểu phim Cinderella Disney chưa? 😱 Phần kết tàn khốc hơn Cinderella nhiều!",
    "caption_bullets": [
        "Tấm mồ côi sống cùng dì ghẻ độc ác và Cám xảo trá",
        "Bụt hiện ra cứu giúp với cá bống huyền thoại",
        "Bống bống bang bang, lên ăn cơm vàng cơm bạc nhà ta",
        "Bầy chim sẻ giúp Tấm nhặt cám với gạo",
        "Đi hội đánh rơi giày, Vua rước về cung",
        "Bị giết oan ức, hóa kiếp 4 lần để trả thù",
        "Kết cuộc tàn khốc của mẹ con Cám"
    ],
    "caption_moral": "Câu chuyện dạy ta: cái thiện thắng cái ác, ác giả ác báo là quy luật không thoát được."
}

# Override motion list for Tấm Cám — scene 1 zoom_in, scene 17 zoom_out, rest static
TAM_CAM_BOOK["motions"] = ["static","zoom_in"] + ["static"] * 15 + ["zoom_out"]

# ================ EXPORT ================
BOOKS = {
    "thach-sanh": THACH_SANH_BOOK,
    "so-dua": SO_DUA_BOOK,
    "cay-tre-tram-dot": CAY_TRE_BOOK,
    "an-khe-tra-vang": AN_KHE_BOOK,
    "son-tinh-thuy-tinh": SON_TINH_BOOK,
    "tam-cam": TAM_CAM_BOOK,
}
