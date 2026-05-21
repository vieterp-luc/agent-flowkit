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
        "Trong kho tàng cổ tích Việt Nam, có một câu chuyện về chàng trai hiền lành bị lừa nhiều lần nhưng cuối cùng vẫn thắng. Phiên bản chi tiết của truyện Thạch Sanh, một câu chuyện cổ tích quen thuộc mà càng nghe lại càng thấm.",
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
        "Trong kho tàng cổ tích Việt Nam, có một câu chuyện về chàng trai sinh ra trong hình hài kỳ lạ. Phiên bản chi tiết của truyện Sọ Dừa, một câu chuyện có nhiều tình tiết bất ngờ thú vị.",
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
        "Trong kho tàng cổ tích Việt Nam, có một câu chuyện về anh nông dân nghèo bị phú ông lừa đảo. Phiên bản chi tiết của truyện Cây Tre Trăm Đốt, một câu chuyện có màn trừng phạt cực kỳ sảng khoái.",
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
        "Hôm nay anh em sẽ nghe lại một câu chuyện cổ tích quen thuộc nhưng đầy bài học, kể về một ông anh tham không đáy và một người em hiền lành đáo để. Truyện Ăn Khế Trả Vàng, một câu chuyện có kết thúc khá là sảng khoái cho những kẻ tham mà không biết đủ. Dân chơi mới hiểu được bài học sâu sắc đằng sau câu chuyện đơn giản này.",
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
        "Trong kho tàng truyền thuyết Việt Nam, có một câu chuyện về cuộc tranh giành tình yêu giữa 2 vị thần khét. Phiên bản chi tiết của truyện Sơn Tinh Thủy Tinh, một câu chuyện có màn combat núi vs nước siêu epic.",
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
        "Thủy Tinh ở dưới biển sâu phải vất vả lắm mới tìm được đủ sính lễ kỳ quặc theo yêu cầu. Khi tới cung vua thì đã muộn vài giờ, công chúa Mị Nương đã được Sơn Tinh rước về núi rồi. Thủy Tinh đứng giữa cung điện trống không, sang chấn nặng nề không nói được câu nào. Hận tới tận xương tủy, Thủy Tinh thề sẽ trả thù Sơn Tinh và cướp lại Mị Nương bằng mọi giá.",
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
        "Trong kho tàng cổ tích Việt Nam, có một câu chuyện về cuộc trả thù tàn khốc nhất sau khi bị mưu hại. Phiên bản chi tiết của truyện Tấm Cám, một câu chuyện có nhiều tình tiết bất ngờ rất khó tin.",
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

# ================ BOOK 7: MAI AN TIÊM ================
MAI_AN_TIEM = _char("Mai An Tiêm", "young Vietnamese man, exiled prince hero: navy solid bomber jacket no print + olive cargo pants, white Air Force sneakers, gold chain, undercut blonde hair, proud self-reliant confident face")
VO_MAI = _char("vợ Mai An Tiêm", "young Vietnamese wife: beige pastel solid áo dài + white Air Force sneakers, long black hair tied in simple bun, gentle resilient face")
CON_MAI = _char("con trai Mai An Tiêm", "young Vietnamese boy around 6 years old: simple brown solid shirt no print + dark shorts, white sneakers, short black hair, innocent curious face")
VUA_HUNG_MAT = _char("Vua Hùng Vương đời 17", "elderly Vietnamese king: red royal robe with aviator sunglasses and Apple Watch, long white beard, sitting on golden throne")
CHIM_QUA = "flock of glossy black crows chim quạ: iridescent dark feathers, sharp golden eyes, beaks carrying small black seeds, dramatic wingspans"
DAO_HOANG = "uninhabited tropical island in Vietnamese sea: white sand beach, palm trees, dense green wild vegetation, rocky outcrops, ocean horizon, isolated lonely atmosphere"
DUA_HAU = "large round watermelon dưa hấu: dark green striped rind, sliced open showing vivid red juicy flesh with black seeds, mouth-watering bright"
COURT_MAI = "ancient Văn Lang royal palace interior: red lacquered wooden columns, hanging red oil lanterns, jade floor tiles, traditional courtiers in áo tứ thân blurred background"

MAI_AN_TIEM_BOOK = {
    "slug": "mai-an-tiem",
    "title": "Mai An Tiêm",
    "story_summary": "Văn Vở Gen Z. Mai An Tiêm phò mã Vua Hùng tự tin sức mình, bị đày ra đảo hoang, tự tay trồng được dưa hấu khắc tên thả biển, cuối cùng được vua hối hận đón về phổ biến giống dưa khắp Văn Lang. Phiên bản kiểu phim Cast Away (2000).",
    "scripts": [
        # Scene 1 — Hook short
        "Trong kho tàng truyền thuyết Việt Nam, có một câu chuyện về chàng phò mã bị đày ra đảo hoang nhưng cuối cùng vẫn thắng đời. Phiên bản chi tiết của truyện Mai An Tiêm, một bài học sâu sắc về sự tự lập và niềm tin vào chính mình.",
        # Scene 2 — Hook plot tease
        "Câu chuyện có vị vua cha nóng tính, có chàng phò mã bị xem là ngạo mạn, có cuộc đày ải ra đảo hoang giữa biển khơi mênh mông. Có đàn quạ thả hạt lạ, có quả dưa hấu đỏ mọng ngọt mát đầu tiên của đất Việt, và một drama hồi cung đầy bài học.",
        # Scene 3 — Body 1: Mai An Tiêm intro + movie poster
        "Ngày xửa ngày xưa, vào đời vua Hùng Vương thứ mười bảy có một chàng trai tên Mai An Tiêm. Anh là phò mã được vua nhận làm con nuôi từ nhỏ, lớn lên thông minh giỏi giang nức tiếng cả triều đình Văn Lang. Mai An Tiêm tự tay làm ra của cải, không cần dựa dẫm vào danh phận hoàng tộc, sống cực kỳ tự lập như một boi phố chính hiệu. Vua Hùng cũng yêu mến anh hết mực, ban cho nhiều bổng lộc và quyền cao chức trọng trong triều.",
        # Scene 4 — Body 2: Câu nói gây họa + ICONIC verbatim lần 1
        "Một hôm trong tiệc lớn, các quan thần khen ngợi Mai An Tiêm có được tất cả là nhờ ơn vua ban tặng. Anh đáp lại tự tin rằng: của mình làm ra mới quý, còn của người khác cho thì chỉ là tạm bợ. Câu nói lập tức bay đến tai vua Hùng, khiến vua nghe xong đứng hình mất mấy giây không nói nên lời. Vua cho rằng phò mã ngạo mạn vô ơn, không biết kính trên nhường dưới, lập tức nổi cơn thịnh nộ ngay tại cung.",
        # Scene 5 — Body 3: Vua đày
        "Vua Hùng giận sôi máu, lập tức ra lệnh đày Mai An Tiêm cùng cả gia đình ra một hòn đảo hoang xa xôi. Vua chỉ cho mang theo một ít lương thực và vài thứ đồ đơn giản, không một viên ngọc nào quý giá. Vua phán rằng để xem phò mã làm ra của cải kiểu gì khi không còn dựa vào triều đình nữa. Mai An Tiêm cúi đầu nhận hình phạt không một lời cãi lại, lặng lẽ thu xếp cùng vợ con bước lên thuyền ra biển khơi.",
        # Scene 6 — Body 4: Lên đảo hoang
        "Sau nhiều ngày lênh đênh trên biển, gia đình Mai An Tiêm cuối cùng cập bến một hòn đảo hoang vu giữa biển khơi mênh mông. Đảo siêu phèn không một bóng người, chỉ có cây cối hoang dại và sóng biển vỗ về bờ cát trắng. Vợ Mai An Tiêm ôm con khóc nức nở vì sợ chết đói chết khát giữa nơi vô tận. Mai An Tiêm bình tĩnh đặt hành lý xuống, ngước nhìn trời rộng rồi tự nhủ phải tìm cách sống sót bằng mọi giá.",
        # Scene 7 — Body 5: Động viên vợ con + dựng lều
        "Mai An Tiêm cầm tay vợ an ủi rằng trời sinh voi sinh cỏ, đảo này tuy hoang nhưng nhất định sẽ có cách. Anh dựng tạm một túp lều tranh bên bờ biển, lấy lá cọ và cành cây ghép lại làm mái che mưa nắng cho cả nhà. Hằng ngày Mai An Tiêm ra biển bắt cá, vào rừng hái rau dại, kiên trì như một dân chơi không bao giờ chịu thua hoàn cảnh. Vợ con thấy chồng cha không nao núng, dần dần cũng vững tâm cùng nhau bắt tay vào lao động.",
        # Scene 8 — Body 6: Khai hoang chăm chỉ
        "Ngày qua ngày, Mai An Tiêm khai hoang được một mảnh đất nhỏ ven biển để trồng cây gì đó dành dụm cho tương lai. Anh đốn cây dựng thêm chuồng nuôi gà, đào ao gần lều để chứa nước mưa dùng cho sinh hoạt. Vợ Mai An Tiêm cùng con phụ chồng làm vườn, cả gia đình ngày càng quen với cuộc sống đơn sơ trên đảo. Nhịp sống tuy vất vả nhưng cả nhà cùng nhau vượt qua, không một lời than thở oán trách số phận hẩm hiu.",
        # Scene 9 — Body 7: Chim quạ thả hạt
        "Một buổi sáng trong lúc Mai An Tiêm đang ra biển bắt cá, bỗng nhiên có một đàn chim quạ đen bay ngang qua đảo. Đàn chim đậu xuống bãi cát nghỉ chân một lát, rồi vỗ cánh bay đi để lại một nắm hạt nhỏ màu đen lạ lẫm. Mai An Tiêm tò mò nhặt hạt lên xem kỹ, thấy chưa từng gặp loại hạt nào như vậy trong đời. Anh ngước nhìn bầu trời rồi tự nghĩ chim đã ăn quả nào đó nơi xa, ngon ơ đem về thử trồng xem sao.",
        # Scene 10 — Body 8: Hạt nảy mầm cây dưa lạ
        "Mai An Tiêm gieo những hạt đen xuống mảnh đất khai hoang, tưới nước đều đặn mỗi sớm mỗi chiều không một ngày bỏ sót. Chỉ vài hôm sau hạt nảy mầm xanh tươi, dây leo bò khắp mặt đất nhanh chóng đến mức không thể tin nổi. Cây ra hoa vàng rồi đậu trái xanh mướt, hình tròn dài lạ mắt to dần lên từng ngày như một loại quả thần kỳ. Vợ chồng Mai An Tiêm khét lẹt mừng rỡ, đợi trái chín hẳn để xem thành quả của công sức bao tháng ngày lao động.",
        # Scene 11 — Body 9: Bổ dưa hấu lần đầu
        "Đến ngày trái chín mọng, Mai An Tiêm hái xuống một quả to nhất bổ ra giữa bãi cát trắng. Bên trong là ruột đỏ thắm mọng nước, hạt đen xen kẽ đẹp lạ thường, hương thơm dịu nhẹ lan tỏa khắp túp lều. Cả gia đình cùng nếm thử lát đầu tiên, vị ngọt mát thấm đẫm xua tan mọi mệt nhọc tích tụ bao ngày. Mai An Tiêm đặt tên cho loại quả này là dưa hấu, đại boss của thành quả lao động giữa hoang đảo cô đơn. Anh tự hào trong lòng vì đây chính là minh chứng cho câu nói trước đây của mình.",
        # Scene 12 — Body 10: Khắc tên thả biển + ICONIC verbatim lần 2
        "Mai An Tiêm có một ý tưởng táo bạo, anh dùng dao khắc tên mình lên vỏ những trái dưa hấu chín mọng. Anh viết rõ chữ Mai An Tiêm và một dòng nhắn ngắn: của mình làm ra mới quý, ai nhặt được xin báo về đất liền giúp. Anh thả các quả dưa khắc tên xuống biển, theo dòng hải lưu trôi dạt đi muôn phương xa. Suốt nhiều ngày sau, dưa hấu trôi qua các ngư dân và thương lái, dần dần lan tới các vùng cửa biển đất liền. Câu chuyện về chàng trai bị đày ngoài đảo nhưng tự trồng được loại quả lạ mau chóng lan truyền khắp Văn Lang.",
        # Scene 13 — Body 11: Vua hối hận đón về
        "Một ngày kia, có sứ giả trình lên vua Hùng một quả dưa hấu lạ nhặt được ngoài cửa biển. Trên vỏ có khắc rõ tên Mai An Tiêm và dòng chữ về câu nói năm xưa, khiến vua đọc xong cười xỉu vì hối hận. Vua nhận ra phò mã ngày xưa nói đúng, không hề ngạo mạn mà là người biết tự lực cánh sinh thực sự. Vua lập tức ra lệnh đoàn sứ giả căng buồm ra đảo, đón Mai An Tiêm cùng cả gia đình trở về cung. Mai An Tiêm mang theo một bao tải hạt dưa hấu về phổ biến cho cả đất nước, từ đó dưa hấu thành đặc sản của Việt Nam.",
        # Scene 14 — Moral
        "Câu chuyện Mai An Tiêm dạy ta rằng giá trị thực sự của con người nằm ở khả năng tự lập, không phải ở những thứ được ban tặng dễ dàng. Khi rơi vào hoàn cảnh khó khăn nhất, nếu ta không bỏ cuộc và kiên trì lao động thì trời đất cũng phải mở đường. Sự tự tin vào bản thân không phải là ngạo mạn, mà là niềm tin vững vàng vào chính sức lực và trí tuệ của mình. Đây không chỉ là truyền thuyết về nguồn gốc dưa hấu, mà còn là bài học muôn đời về phẩm giá và sức mạnh nội tại của con người Việt Nam.",
    ],
    "image_prompts": [
        # 1 — Hook atmospheric
        f"Atmospheric establishing wide shot: ancient Văn Lang coastal village at dawn, fishing boats moored by shore, mist rising over rice paddies, distant green mountains in background, no characters visible, mood-setting cinematic.",
        # 2 — Hook movie poster Cast Away style split
        f"Movie-poster composition: {MAI_AN_TIEM} on LEFT half in dignified posture with royal palace setting behind, {DAO_HOANG} on RIGHT half deserted with palm trees and crashing ocean waves, split lighting dramatic high-contrast, fairy-tale poster framing.",
        # 3 — Body 1: royal court intro
        f"Royal court scene: {MAI_AN_TIEM} standing confidently before {VUA_HUNG_MAT} on golden throne, traditional officials bowed around, {COURT_MAI}, warm golden lighting two-shot composition.",
        # 4 — Body 2: banquet shock câu nói
        f"Royal banquet scene: {MAI_AN_TIEM} raising wine cup speaking proudly with chin lifted, surrounding court officials whispering shocked covering mouths, {VUA_HUNG_MAT} face freezing in surprise on golden throne in background, {COURT_MAI}, dramatic spotlight on Mai An Tiêm.",
        # 5 — Body 3: vua đày
        f"Court of judgment: {VUA_HUNG_MAT} pointing dramatically toward open palace doors revealing ocean horizon outside, {MAI_AN_TIEM} kneeling head bowed accepting punishment, {VO_MAI} holding {CON_MAI} crying nearby, {COURT_MAI}, cold blue dramatic lighting.",
        # 6 — Body 4: arrival deserted island
        f"Arrival at deserted island: small wooden boat beached on white sand shore, {MAI_AN_TIEM} stepping off carrying basic supplies and bamboo basket, {VO_MAI} holding {CON_MAI} crying behind him, {DAO_HOANG}, midday harsh sun isolation mood.",
        # 7 — Body 5: hut consoling
        f"Primitive island hut scene: {MAI_AN_TIEM} kneeling next to {VO_MAI} gently holding her hands consoling her, {CON_MAI} sitting on sand beside them looking up curiously, simple thatched bamboo hut behind, {DAO_HOANG}, warm late afternoon golden hour lighting.",
        # 8 — Body 6: survival farming
        f"Daily survival scene: {MAI_AN_TIEM} digging soil with wooden hoe in cleared patch of island ground, {VO_MAI} carrying woven water bucket from rain pond, {CON_MAI} feeding small chickens nearby, simple thatched hut visible behind, {DAO_HOANG}, hopeful perseverance mood.",
        # 9 — Body 7: chim quạ thả hạt
        f"Mysterious bird scene: {CHIM_QUA} flock landing on white sand beach scattering small black seeds, {MAI_AN_TIEM} watching from distance with curious expression carrying fishing net, {DAO_HOANG}, magical lighting hint of cyan glow on seeds.",
        # 10 — Body 8: garden growing watermelon vines
        f"Lush garden growing scene: green watermelon vines sprawling across cleared patch of island ground with yellow flowers blooming, several large round green-striped watermelons growing among leaves, {MAI_AN_TIEM} watering plants with bamboo bucket with awe pride expression, {DAO_HOANG} background.",
        # 11 — Body 9: family harvest first watermelon
        f"Family harvest scene: {MAI_AN_TIEM} cutting open a large {DUA_HAU} with bamboo knife revealing vivid red flesh, {VO_MAI} and {CON_MAI} smiling tasting the first juicy slice together, simple thatched hut behind, {DAO_HOANG} background, warm joyful golden lighting.",
        # 12 — Body 10: carve name + thả biển (ICONIC)
        f"Beach send-off scene: {MAI_AN_TIEM} crouched on white sand carefully carving his name onto green watermelon rind with bamboo knife, several carved watermelons floating in shallow waves nearby drifting out to open sea, {DAO_HOANG}, contemplative determined expression, sunset orange-gold lighting.",
        # 13 — Body 11: vua nhận dưa hối hận
        f"Royal court revelation: {VUA_HUNG_MAT} sitting on golden throne holding a {DUA_HAU} with carved name clearly visible, expression shifting from skepticism to deep regret with hand on chin, court messenger kneeling presenting more carved watermelons, {COURT_MAI}, warm soft repentant lighting.",
        # 14 — Moral homecoming distribute seeds
        f"Closing peaceful homecoming: {MAI_AN_TIEM} standing in Văn Lang village marketplace distributing watermelon seeds to crowd of farmers, {VO_MAI} and {CON_MAI} smiling beside him, villagers eagerly taking seeds with grateful faces, warm amber golden sunset palette, hopeful prosperous oil-painting mood.",
    ],
    "motions": ["static","zoom_in","static","static","static","static","static","static","static","static","zoom_out","static","pan_right","static","zoom_out"],
    "caption_hook": "Anh em nghe truyện Mai An Tiêm kiểu phim Cast Away chưa? 🍉🏝️ Phò mã bị đày đảo hoang, tự tay trồng dưa hấu lan khắp Việt Nam!",
    "caption_bullets": [
        "Mai An Tiêm phò mã Vua Hùng, tự tin vào sức mình",
        "Câu nói 'của mình làm ra mới quý' khiến vua nổi giận",
        "Cả gia đình bị đày ra đảo hoang giữa biển khơi",
        "Đàn quạ thả hạt đen lạ trên bãi cát",
        "Mai An Tiêm trồng được dưa hấu đầu tiên — đỏ mọng ngọt mát",
        "Khắc tên thả dưa xuống biển trôi về đất liền",
        "Vua Hùng nhặt được, hối hận đón về phổ biến dưa hấu khắp Văn Lang"
    ],
    "caption_moral": "Câu chuyện dạy ta: giá trị thực sự của con người nằm ở khả năng tự lập, kiên trì lao động và niềm tin vững vàng vào chính mình."
}

# ================ BOOK 8: CHÚ CUỘI CUNG TRĂNG ================
CHU_CUOI = _char("Chú Cuội", "young Vietnamese woodcutter: forest-green solid hoodie no print + olive cargo pants, brown work boots, gold chain, undercut black hair, kind honest face carrying small wooden axe")
VO_CUOI = _char("vợ chú Cuội", "young Vietnamese wife from rich family: pink pastel solid áo dài + white Air Force sneakers, long black hair tied simple, gentle elegant face")
PHU_ONG_CUOI = _char("phú ông bố vợ Cuội", "middle-aged wealthy Vietnamese man: red royal áo dài with gold trim, aviator sunglasses, gold chain, thin slick beard, generous welcoming face")
BUT_CUOI = _char("Bụt deity", "kind elderly Buddhist deity: white flowing robe with neon cyan glow aura, long silver beard, holding wooden staff, soft golden halo")
COP_ME = "adult Vietnamese tiger mother cọp mẹ: orange-black striped fur, powerful muscular body, protective stance, fierce loving eyes"
COP_CON = "Vietnamese tiger cub cọp con: small fluffy orange-black striped fur, big innocent eyes, weak injured body lying on the ground"
CAY_DA_THAN = "massive ancient magical banyan tree cây đa thần: thick gnarled trunk, sprawling aerial roots, dense leafy canopy glowing with mystical cyan and gold magical aura, ethereal golden particles floating around leaves"
LANG_QUE_CUOI = "rural Vietnamese village setting: bamboo huts with thatched roofs, rice paddies, banana trees, dirt paths, distant mountains, peaceful countryside"
CUNG_TRANG = "lunar palace surface cung trăng: vast crater landscape with glowing crystalline rocks, distant stars in black cosmic sky, ethereal silver-blue ambient lighting, earth visible distant blue marble in background"

CHU_CUOI_BOOK = {
    "slug": "chu-cuoi-cung-trang",
    "title": "Sự Tích Chú Cuội Cung Trăng",
    "story_summary": "Văn Vở Gen Z. Chú Cuội tiều phu nghèo tốt bụng phát hiện cây đa thần cứu mạng, nổi tiếng cưới vợ giàu. Vợ quên rule đái nhầm bên tây cây đa, cây bay lên cung trăng kéo theo Cuội. Phiên bản kiểu phim Interstellar (2014).",
    "scripts": [
        # Scene 1 — Hook short
        "Trong kho tàng cổ tích Việt Nam, có một câu chuyện về chàng tiều phu vô tình bay lên cung trăng vì một cái quên ngớ ngẩn của vợ. Phiên bản chi tiết của truyện Chú Cuội Cung Trăng, một câu chuyện có cả drama lẫn bài học cuộc đời sâu sắc.",
        # Scene 2 — Hook plot tease
        "Câu chuyện có cây đa thần kỳ chữa được người chết sống lại, có chàng tiều phu hiền lành nổi tiếng khắp vùng. Có cô vợ hậu đậu lú một phen, có cây đa bay lên trời mang theo cả người ngồi gốc cây, và lý do vì sao cứ rằm là ta thấy bóng người trên mặt trăng.",
        # Scene 3 — Body 1: Cuội tiều phu intro + movie mapping
        "Ngày xửa ngày xưa ở một làng quê nghèo, có chàng trai tên Cuội sống bằng nghề đốn củi qua ngày. Cuội mồ côi cha mẹ từ nhỏ, sống một mình trong túp lều nhỏ ven rừng già hiu quạnh. Tuy nghèo nhưng Cuội tốt bụng và lương thiện, đối xử tử tế với mọi sinh vật xung quanh không phân biệt người hay vật. Hằng ngày anh vác rìu vào rừng sâu chặt củi mang ra chợ bán, sống cuộc đời đơn giản như một boi phố chân chính dù nghèo khó.",
        # Scene 4 — Body 2: Cuội gặp cọp con bị thương
        "Một hôm như thường lệ, Cuội vác rìu đi sâu vào rừng tìm gỗ tốt thì bỗng nghe tiếng kêu nhỏ lạ thường. Anh lần theo tiếng kêu đến một bụi cỏ rậm, phát hiện một con cọp con bị thương nằm thoi thóp dưới gốc cây. Cuội thương quá định cứu giúp, nhưng chợt nghĩ tới cọp mẹ có thể trở về thì nguy hiểm vô cùng. Anh đành lui ra xa nấp sau bụi cây để xem tình hình ra sao, đứng hình không dám rời đi vì lo cho con vật tội nghiệp.",
        # Scene 5 — Body 3: cọp mẹ về đắp lá cứu cọp con
        "Không lâu sau cọp mẹ to lớn quay về, gầm vang động cả rừng làm Cuội đứng nép tim đập thình thịch. Cọp mẹ thấy con bị thương thì lao đến, không gầm thét nữa mà cẩn thận ngắt vài chiếc lá từ một cây đa cổ thụ gần đó. Cọp mẹ nhai nát lá đa rồi đắp lên vết thương cọp con cẩn thận, chỉ vài phút sau cọp con bỗng tỉnh dậy chạy nhảy bình thường như chưa hề bị gì. Cuội cười xỉu vì kinh ngạc, đợi cọp mẹ con đi xa rồi mới dám lò dò đến gần cây đa quan sát kỹ.",
        # Scene 6 — Body 4: nhổ cây đa + ICONIC verbatim lần 1
        "Cuội nhận ra đây là cây đa thần kỳ có thể chữa được mọi vết thương kể cả người chết sống lại. Anh quyết định nhổ cả cây đa mang về nhà trồng để cứu giúp người làng nghèo khổ khắp nơi. Vừa nhổ xong, có một ông lão bụt râu tóc bạc phơ hiện ra dặn dò kỹ lưỡng. Bụt phán rõ ràng: có đái thì đái bên đông, chớ đái bên tây cây dông lên trời. Cuội gật đầu thuộc lòng câu thần chú, vác cả gốc lẫn cành về làng trồng trước sân nhà mình ngay trong đêm khuya.",
        # Scene 7 — Body 5: cứu chó chết + nổi tiếng
        "Hôm sau Cuội thử nghiệm sức mạnh cây đa với con chó vàng nhà mình vừa mới chết. Anh ngắt vài chiếc lá đa nhai nát đắp lên người chó, chỉ một lát sau chó vàng bỗng vẫy đuôi sống lại tỉnh táo. Tin Cuội có cây đa cứu mạng người chết lan ra khắp vùng, ai có người thân vừa qua đời đều tìm đến cầu cứu. Cuội tốt bụng cứu hết không lấy một đồng tiền nào, dần dần trở thành idol quốc dân của cả vùng quê chỉ trong vài tháng.",
        # Scene 8 — Body 6: cứu con gái phú ông + cưới
        "Một hôm phú ông giàu nhất vùng có cô con gái duy nhất bỗng nhiên mất sớm vì bệnh nặng. Phú ông nghe danh Cuội liền cho người mời gấp đến cứu, hứa nếu cứu được sẽ gả con gái làm vợ ngay. Cuội đến nơi ngắt lá đa thần đắp lên người cô gái, cô bỗng tỉnh dậy hồng hào như chưa hề mất. Phú ông giữ đúng lời hứa giang hồ gả con gái xinh đẹp cho Cuội, anh lú một phen vì vận may bất ngờ đổ xuống đầu mình.",
        # Scene 9 — Body 7: sống hạnh phúc + nhắc vợ ICONIC verbatim lần 2
        "Cuội và vợ sống hạnh phúc trong căn nhà nhỏ có cây đa thần trước sân, đời sống ngày càng sung túc. Cuội cẩn thận dặn vợ về quy tắc Bụt đã phán năm xưa: có đái thì đái bên đông, chớ đái bên tây cây dông lên trời. Vợ Cuội cười gật đầu hứa nhớ rõ ràng, không bao giờ dám phạm vào điều cấm kỵ này. Cả gia đình sống yên ổn nhiều năm, Cuội tiếp tục dùng lá đa cứu người gần xa flex tài năng nhân ái mỗi ngày.",
        # Scene 10 — Body 8: vợ Cuội quên + đổ nước bên tây
        "Một hôm Cuội đi rừng chặt củi từ sáng sớm, để vợ ở nhà một mình lo việc cơm nước. Trưa hôm ấy vợ Cuội bỗng nhiên đau bụng dữ dội, vội vàng chạy ra sân tìm chỗ giải quyết gấp. Trong lúc luống cuống vội vàng quên hết mọi lời chồng dặn, vợ Cuội ngồi xuống đại ngay bên tây gốc cây đa. Vừa làm xong vợ chợt nhớ ra điều cấm kỵ năm xưa, mặt cắt không còn giọt máu đứng hình vì biết mình đã phạm vào đại điều kiêng.",
        # Scene 11 — Body 9: cây đa rung chuyển nhổ rễ bay
        "Vừa lúc đó cây đa thần bắt đầu rung chuyển dữ dội, từng chiếc lá xao động như có cơn bão lớn ập đến. Mặt đất quanh gốc cây bắt đầu nứt nẻ, rễ cây từ từ bật lên khỏi lòng đất một cách kỳ lạ chưa từng thấy. Cây đa khổng lồ bắt đầu nhấc bổng lên không trung, bay lơ lửng cao dần như có sức hút từ trời cao. Vợ Cuội đứng chết lặng nhìn cây đa bay lên, không biết phải làm sao để cản lại điều này.",
        # Scene 12 — Body 10: Cuội về thấy cây bay
        "Đúng lúc đó Cuội từ rừng vác củi trở về, vừa bước qua cổng làng thì thấy cảnh tượng kinh hoàng. Cây đa thần đang bay lên cao mỗi lúc một xa, sắp lên đến tầng mây mỏng tang trên đỉnh trời. Cuội bỏ rơi gánh củi lao về như tên bắn, chạy bán sống bán chết đến tận sân nhà. Anh nhảy bổ lên nắm chặt một rễ cây đa đang lơ lửng cuối cùng, không chịu buông tay vì tiếc báu vật cả đời mới có được.",
        # Scene 13 — Body 11: Cuội bị kéo lên cung trăng
        "Cây đa thần bay lên không trung càng lúc càng cao, kéo theo Cuội vẫn nắm chặt rễ không chịu buông tay. Cuội bay lên qua các tầng mây trắng bồng bềnh, qua các ngôi sao lấp lánh trên bầu trời đêm bao la vô tận. Cuối cùng cây đa cùng Cuội cập bến cung trăng xa xôi giữa vũ trụ mênh mông, không cách nào quay về trái đất được nữa. Cuội đành chịu thua hoàn cảnh, ngồi xuống dưới gốc cây đa trên mặt trăng mà nhìn về quê hương dưới đất bằng đôi mắt buồn vô tận.",
        # Scene 14 — Moral
        "Câu chuyện Chú Cuội Cung Trăng dạy ta rằng đôi khi chỉ một phút lơ đãng cũng đủ thay đổi cả số phận con người. Lời dặn dò của người thân yêu không bao giờ là thừa, mỗi quy tắc đều có lý do riêng đáng để ta lắng nghe nghiêm túc. Báu vật quý giá nhất không phải vàng bạc hay quyền lực, mà là sự cẩn trọng và lòng biết ơn với những điều mình đang có. Mỗi đêm rằm trông trăng, ta lại nhớ về bài học muôn thuở về sự cẩn thận và trân quý những gì giản dị quanh mình.",
    ],
    "image_prompts": [
        # 1 — Hook atmospheric moonlit village
        f"Atmospheric establishing wide shot: ancient Vietnamese rural village at midnight under full moon, mist rising from rice paddies, single massive banyan tree silhouette in distance, no characters visible, mystical mood-setting cinematic.",
        # 2 — Hook movie poster Interstellar split
        f"Movie-poster composition: {CHU_CUOI} on LEFT half with woodcutter axe and forest backdrop, {CUNG_TRANG} crater surface with banyan tree silhouette on RIGHT half, dramatic split lighting earth-vs-cosmos, fairy-tale poster framing.",
        # 3 — Body 1: Cuội tiều phu intro walking
        f"Rural daily scene: {CHU_CUOI} carrying bundle of firewood on shoulder walking through {LANG_QUE_CUOI} at dawn, simple thatched hut visible behind, warm morning golden light, peaceful contemplative mood.",
        # 4 — Body 2: Cuội gặp cọp con bị thương
        f"Dense forest scene: {CHU_CUOI} crouching cautiously behind bush peering at {COP_CON} lying injured under tall tree, dappled sunlight through canopy, suspenseful mood with hint of distant mystical green glow.",
        # 5 — Body 3: cọp mẹ đắp lá đa cứu cọp con
        f"Magical forest scene: {COP_ME} carefully chewing leaves and pressing them onto {COP_CON}'s wounds, {CAY_DA_THAN} glowing mystically nearby with golden particles, {CHU_CUOI} hidden behind bush wide-eyed in awe, dramatic golden mystical lighting.",
        # 6 — Body 4: Cuội nhổ cây + Bụt phán rule
        f"Mystical scene: {CHU_CUOI} pulling up the entire {CAY_DA_THAN} with magical golden roots glowing, {BUT_CUOI} appearing in mist beside him with one finger raised giving sacred warning gesture, dense ancient forest background, mystical cyan-gold lighting.",
        # 7 — Body 5: cứu chó villagers gathering
        f"Village front yard scene: {CHU_CUOI} applying glowing magical banyan leaves to a previously deceased yellow village dog now waking up wagging tail, {CAY_DA_THAN} planted in front yard of simple thatched hut, neighboring villagers gathering watching in awe, warm afternoon light.",
        # 8 — Body 6: cứu vợ phú ông + cưới
        f"Rich household interior: {CHU_CUOI} applying glowing magical banyan leaves to {VO_CUOI} lying on bed just waking up, {PHU_ONG_CUOI} standing nearby clasping hands in gratitude, lavish room with red lacquered furniture and gold accents, warm golden lighting.",
        # 9 — Body 7: domestic happy + nhắc rule
        f"Domestic happy scene: {CHU_CUOI} and {VO_CUOI} sitting together on wooden bench in front of simple thatched home, {CAY_DA_THAN} glowing softly in front yard between them, {CHU_CUOI} pointing toward east side of tree explaining warning, warm late afternoon golden hour, sweet mood.",
        # 10 — Body 8: vợ Cuội đổ nước bên tây
        f"Dramatic mistake scene: {VO_CUOI} standing on west side of {CAY_DA_THAN} pouring a wooden bucket of dirty wash water onto roots with worried regretful expression hand to mouth realizing her mistake too late, dimly lit overcast afternoon, subtle ominous wind ruffling the leaves.",
        # 11 — Body 9: cây đa nhổ rễ bay lên
        f"Magical uprooting scene: {CAY_DA_THAN} mid-air rising up from cracked earth with golden roots glowing dangling, dust and leaves swirling around the tree, {VO_CUOI} standing below looking up in horror with arms raised helplessly, dramatic dark stormy sky above, cinematic action.",
        # 12 — Body 10: Cuội về thấy cây bay
        f"Action scene: {CHU_CUOI} dropping his bundle of firewood mid-run racing through {LANG_QUE_CUOI} toward home, {CAY_DA_THAN} visible flying mid-air above the hut in distance, panicked desperate expression, motion blur, dramatic golden hour light.",
        # 13 — Body 11: Cuội bay lên cung trăng
        f"Cosmic ascension scene: {CHU_CUOI} clinging to dangling golden roots of {CAY_DA_THAN} as it floats higher through stars and clouds above earth toward {CUNG_TRANG}, magical golden particle trail, swirling cyan starlight nebula, awe and dread expression.",
        # 14 — Moral iconic silhouette
        f"Iconic closing scene: {CHU_CUOI} sitting alone under {CAY_DA_THAN} on {CUNG_TRANG} silhouette against full moon, looking down at distant blue earth visible in night sky below, contemplative bittersweet expression, ethereal silver-blue lighting, oil-painting feel hopeful melancholy mood.",
    ],
    "motions": ["static","zoom_in","static","pan_right","static","static","static","static","static","static","static","zoom_out","pan_right","zoom_out","static"],
    "caption_hook": "Anh em đã nghe Chú Cuội Cung Trăng kiểu phim Interstellar chưa? 🌕🌳 Tiều phu hiền lành lên cung trăng vì vợ quên một câu thần chú!",
    "caption_bullets": [
        "Chú Cuội tiều phu nghèo, tốt bụng với mọi sinh vật",
        "Cọp mẹ đắp lá đa cứu cọp con — Cuội phát hiện cây đa thần",
        "Bụt phán rule kiêng kỵ: có đái thì đái bên đông, chớ đái bên tây",
        "Cuội cứu chó cứu con gái phú ông, cưới vợ giàu",
        "Vợ Cuội quên rule, đại nhầm bên tây cây đa",
        "Cây đa thần rung chuyển nhổ rễ bay lên trời",
        "Cuội nắm rễ bay theo lên cung trăng — mỗi đêm rằm còn thấy bóng"
    ],
    "caption_moral": "Câu chuyện dạy ta: lời dặn dò của người thân yêu không bao giờ là thừa, cẩn thận và biết ơn những gì giản dị quanh mình."
}

# ================ BOOK 9: BÁNH CHƯNG BÁNH DÀY ================
LANG_LIEU = _char("Lang Liêu hoàng tử thứ 18", "young Vietnamese prince humble: beige plain solid áo dài no royal trim + brown cargo pants, white sneakers, small modest gold chain, undercut black hair, gentle humble determined face")
VUA_HUNG_BCBD = _char("Vua Hùng Vương đời 6", "elderly Vietnamese king: dark red royal robe with gold trim, aviator sunglasses, Apple Watch, long white beard, sitting on golden throne, thoughtful patriarchal expression")
TIEN_ONG_BCBD = _char("Tiên ông in dream", "elderly celestial fairy deity: white flowing celestial robe with golden cyan glow aura, long silver-white beard reaching waist, floating in mist with golden halo, kindly wise expression holding wooden staff")
HOANG_TU_NHA_GIAU = "group of arrogant rich Vietnamese princes hoàng tử: oversized solid bomber jackets in red blue gold no print, multiple gold chains, aviator sunglasses, slicked black hair, smug arrogant expressions holding rare ingredients"
COURT_BCBD = "ancient Văn Lang royal palace interior: red lacquered wooden columns, hanging red oil lanterns, jade floor tiles, traditional courtiers in áo tứ thân blurred background, gold and red opulent decor"
LANG_QUE_BCBD = "peaceful rural Vietnamese village: bamboo huts with thatched roofs, golden rice paddies stretching to horizon, banana trees, dirt paths, distant green mountains, harvest season abundance"
BANH_CHUNG = "square Vietnamese rice cake bánh chưng: dark green dong leaves wrapping a perfectly square cake, tied with bamboo string lạt, golden glutinous rice inside with green mung bean and pork filling visible in cross-section"
BANH_DAY = "round Vietnamese rice cake bánh dày: pure white sticky rice cake shaped as smooth round disc, glossy surface, placed on green banana leaf"

BANH_CHUNG_BOOK = {
    "slug": "banh-chung-banh-day",
    "title": "Sự Tích Bánh Chưng Bánh Dày",
    "story_summary": "Văn Vở Gen Z. Vua Hùng đời 6 mở cuộc thi truyền ngôi, 22 hoàng tử dâng sơn hào hải vị. Lang Liêu con thứ 18 mồ côi mẹ, nằm mộng được tiên ông chỉ cách làm bánh chưng bánh dày từ gạo nếp, thắng cuộc thi truyền ngôi. Phiên bản kiểu phim Ratatouille (2007).",
    "scripts": [
        # Scene 1 — Hook short
        "Trong kho tàng truyền thuyết Việt Nam, có một cú lội ngược dòng đầy drama của chàng hoàng tử mồ côi, người đã thắng cuộc thi đầu bếp hoàng gia chỉ bằng món ăn quê mùa nhất quả đất. Khi Vua Hùng già sắp truyền ngôi, trong lúc hai mươi mấy người anh em đua nhau dâng sơn hào hải vị, thì chàng hoàng tử thứ 18 lại được tiên ông chỉ điểm cách làm bánh từ hạt gạo nếp. Hãy cùng xem lại sự tích Bánh Chưng Bánh Dày, vì đây là một bài học sâu sắc về sự khiêm tốn mà đến nay vẫn cực kỳ thấm",
        # Scene 3 — Body 1: Vua Hùng setup casting
        "Ngày xửa ngày xưa vào đời Vua Hùng Vương thứ sáu, ông vua đã già và tới giai đoạn phải chọn người kế vị. Vấn đề là vua có nguyên một đội hai mươi mấy hoàng tử, mỗi ông một tài năng riêng, không ông nào kém ông nào. Vua không phải dạng cha truyền con nối theo công thức, vua thấy ông nào xứng nhất thì cho. Cuối cùng vua nghĩ ra một cách công bằng kiểu thi tuyển hoàng gia, tôi gọi vui là MasterChef Văn Lang phiên bản bốn nghìn năm trước Công nguyên.",
        # Scene 4 — Body 2: Luật chơi + 22 hoàng tử chuẩn bị
        "Luật chơi đơn giản, mỗi hoàng tử có một khoảng thời gian nhất định để tự đi tìm hoặc tự làm ra một món ăn dâng cúng tổ tiên. Món nào hợp ý vua cha nhất, ngôi báu trao tay luôn không bàn cãi. Tin vừa thông báo xong thì cả cung nháo nhào lên, mỗi ông một kế hoạch riêng. Ông thì gọi gia nhân lên rừng săn hươu nai báo gấm, ông thì sai người xuống biển bắt cá quý tôm hùm, ông thì cho người đi khắp các nước lân bang tìm gia vị siêu hiếm flex đẳng cấp.",
        # Scene 5 — Body 3: Lang Liêu profile
        "Trong giữa cái biển hoàng tử chen nhau khoe tài chính ấy thì có một ông đứng góc, đó là hoàng tử Lang Liêu. Đây là con thứ mười tám của Vua Hùng, mẹ mất sớm từ khi Lang Liêu còn rất nhỏ, không được đại gia đình nâng đỡ như mấy ông anh con dòng chính. Profile của Lang Liêu thì gần như đối lập một trăm tám mươi độ với hình ảnh hoàng tử mà anh em hay tưởng tượng. Em không có gia nhân riêng, không có ngân khố vung tiền săn đồ quý, không có quan hệ thương gia trong lẫn ngoài nước.",
        # Scene 6 — Body 4: Lang Liêu buồn không có gì để dâng
        "Nghe vua cha ra đề bài xong thì các ông anh xôn xao lên kế hoạch, còn Lang Liêu thì ngồi yên một góc với tâm trạng nặng trĩu. Anh biết quá rõ mình không có bất cứ thứ gì để cạnh tranh với hai mươi đối thủ kia. Trong khi mấy ông anh tấp nập xe ngựa chở hàng hiếm về cung thì Lang Liêu chỉ đi tới đi lui trong căn nhà nhỏ nhìn ra cánh đồng lúa vàng. Cảm giác bị bỏ lại phía sau ám ảnh vô cùng, không có ý tưởng nào sáng tạo để vượt mặt mấy ông anh giàu nứt đố đổ vách.",
        # Scene 7 — Body 5: Tiên ông hiện ra + ICONIC verbatim lần 1
        "Đêm hôm đó Lang Liêu nằm trằn trọc trên giường nghĩ ngợi mãi, cuối cùng kiệt sức rồi cũng thiếp đi giữa khuya. Trong giấc mộng thì có một ông tiên râu tóc bạc phơ hiện ra giữa làn mây trắng, ánh hào quang vàng rực chiếu khắp căn nhà nhỏ. Tiên ông cười hiền từ rồi nói rõ ràng từng chữ một: trong trời đất không có gì quý bằng hạt gạo, vì gạo là thứ nuôi sống con người. Lang Liêu nghe vậy thì tỉnh ngộ ngay lập tức, ngồi bật dậy lắng nghe tiên ông tiếp tục dặn dò.",
        # Scene 8 — Body 6: Tiên ông dạy công thức 2 bánh
        "Tiên ông không dừng ở đây mà còn hướng dẫn chi tiết luôn, kiểu một anh streamer cooking đang giảng công thức cho viewer. Tiên dặn hãy lấy gạo nếp dẻo làm thành hai loại bánh, một loại hình vuông tượng trưng cho mặt đất nuôi dưỡng muôn loài, một loại hình tròn tượng trưng cho bầu trời che chở vạn vật. Bánh vuông gói trong lá dong xanh, bên trong có nhân đậu xanh thịt lợn biểu hiện cho những gì con người trồng nuôi được. Bánh tròn làm từ gạo nếp giã nhuyễn nguyên chất biểu hiện sự thuần khiết của trời cao.",
        # Scene 9 — Body 7: Lang Liêu tỉnh dậy chọn nguyên liệu
        "Lang Liêu giật mình tỉnh dậy giữa đêm khuya, đầu vẫn còn nguyên cảm giác công thức nóng hổi từ tiên ông vừa dặn. Sáng hôm sau anh bật dậy lập tức bắt tay vào việc, không một phút trì hoãn. Đầu tiên anh ra đồng tự tay chọn từng hạt gạo nếp dẻo thơm nhất, hạt nào lép thì bỏ ra ngay không tiếc tay. Tiếp đó anh đi rừng hái lá dong xanh mướt, chọn lá to bản không rách không sâu, kích thước vừa đúng để gói được cái bánh vuông đẹp mắt. Lang Liêu xin một con lợn béo nhất làng thui sạch lông cẩn thận.",
        # Scene 10 — Body 8: Gói bánh chưng + giã bánh dày
        "Khi mọi nguyên liệu sẵn sàng, Lang Liêu tự tay gói chiếc bánh chưng đầu tiên trong lịch sử Việt Nam, lá dong xếp chéo theo bốn cạnh, gạo nếp rải đều, nhân đậu xanh thịt lợn cho vào giữa, rồi gói lại vuông vức từng góc buộc dây lạt chắc nịch. Bánh dày thì khác, anh nấu chín gạo nếp rồi cho vào cối đá giã nhuyễn bằng chày gỗ. Giã đến khi gạo trở thành khối dẻo mịn không còn hạt rời, anh mới nặn thành những chiếc bánh tròn trịa đẹp mắt. Trải qua mấy ngày cặm cụi không nghỉ tay, Lang Liêu cuối cùng cũng có một mâm bánh đẹp đến mức chính anh cũng đứng hình khi nhìn lại thành quả của mình.",
        # Scene 11 — Body 9: Ngày final + hoàng tử khác dâng sơn hào
        "Ngày hẹn đến, các hoàng tử lũ lượt mang sản phẩm vào cung dâng vua cha, cảnh tượng ngoài đại sảnh nhìn không khác gì hội chợ ẩm thực quốc tế. Một ông khiêng nguyên con hươu nai quý hiếm vừa săn được tận rừng sâu, lông còn óng mượt như mới ra từ phim quảng cáo. Một ông khác bưng mâm cua hùm tôm hùm tươi rói còn nhảy tanh tách trên đĩa bạc. Có ông dâng cả một bàn sơn hào với mấy loại gia vị quý hiếm chỉ tìm được ở mấy xứ xa nghìn dặm, mỗi ông một kiểu flex khác nhau cực kỳ căng.",
        # Scene 12 — Body 10: Lang Liêu dâng bánh + hoàng tử khác cười khẩy
        "Vua Hùng ngồi trên ngai vàng bình thản quan sát hết một lượt, mặt không lộ vẻ vui hay buồn, cứ giống một giám khảo MasterChef siêu khó tính. Vua nếm món gì cũng chỉ gật nhẹ rồi cho đặt sang một bên, không khen mà cũng không chê một lời. Đến lượt Lang Liêu thì anh khiêm tốn bưng ra một mâm chỉ có hai loại bánh trông cực kỳ đơn giản. Các hoàng tử khác liếc qua thấy thì cười khẩy, có ông còn buông một câu xỉa cười xỉu: chú em này không có gì thì nên rút lui cho đỡ mất mặt.",
        # Scene 13 — Body 11: Vua nếm + phán quyết + ICONIC verbatim lần 2
        "Vua nhìn mâm bánh lạ thì cau mày hỏi đây là món gì vậy. Lang Liêu cúi đầu thưa rõ ràng: thưa vua cha, đây là bánh chưng bánh dày con tự làm từ gạo nếp đất nhà. Trong trời đất không có gì quý bằng hạt gạo, bánh chưng hình vuông tượng trưng cho đất, bánh dày hình tròn tượng trưng cho trời. Vua nghe xong gật gù cầm dao cắt một miếng bánh chưng ăn thử, vị dẻo thơm bùi ngậy hòa quyện làm vua mắt sáng rực hài lòng. Vua tuyên bố ngay tại đại sảnh: ta đã quyết, ngai vàng truyền cho Lang Liêu, kẻ duy nhất biết quý trọng những gì trời đất ban tặng cho con người.",
        # Scene 14 — Moral
        "Câu chuyện Bánh Chưng Bánh Dày dạy ta một bài học vô cùng sâu sắc, đó là giá trị thực sự của con người không nằm ở sự xa hoa cầu kỳ, mà ở khả năng trân quý và tôn vinh những điều giản dị nhất xung quanh mình. Trong khi các hoàng tử khác chạy theo những thứ quý hiếm xa xôi, Lang Liêu lại biết nhìn xuống chính mảnh đất quê hương để tìm ra báu vật. Cứ mỗi dịp Tết đến, khi gói chiếc bánh chưng vuông vắn buộc bằng dây lạt, người Việt lại nhớ về truyền thuyết này và tự nhắc nhau rằng hạnh phúc nằm trong chính cái nồi bánh chưng đỏ lửa đêm giao thừa.",
    ],
    "image_prompts": [
        # 1 — Hook (single, merged) movie poster Ratatouille split
        f"Movie-poster composition: {LANG_LIEU} on LEFT half humble holding a simple wooden tray with two plain rice cakes ({BANH_CHUNG} and {BANH_DAY}), RIGHT half showing piles of luxurious sơn hào hải vị (whole roasted deer, lobsters, exotic spices) under elaborate gold chandeliers, split lighting underdog vs elite contrast, fairy-tale poster framing.",
        # 3 — Body 1: Vua Hùng court setup
        f"Royal court scene: {VUA_HUNG_BCBD} sitting on golden throne thoughtful pondering succession, surrounded by silent courtiers and ministers, {COURT_BCBD}, warm golden lighting, regal patriarchal mood.",
        # 4 — Body 2: 22 hoàng tử chuẩn bị lên rừng xuống biển
        f"Dynamic montage scene: {HOANG_TU_NHA_GIAU} departing in different directions, one prince hunting deer in mountain forest, another on coastal boat reaching for sea creatures, another negotiating with foreign merchants for spices in marketplace, ancient Văn Lang setting, energetic preparation mood.",
        # 5 — Body 3: Lang Liêu profile humble walking village
        f"Rural humble scene: {LANG_LIEU} walking through {LANG_QUE_BCBD} at golden hour with farmers harvesting rice in background, simple thatched hut visible, peaceful but pensive mood, warm amber lighting contemplative.",
        # 6 — Body 4: Lang Liêu buồn nhìn cánh đồng
        f"Emotional scene: {LANG_LIEU} sitting alone on wooden bench outside his simple thatched home, staring out at golden rice paddies at sunset with sad pensive expression hand on chin, soft melancholy warm lighting, {LANG_QUE_BCBD} background.",
        # 7 — Body 5: Tiên ông hiện ra giấc mộng
        f"Mystical dream scene: {LANG_LIEU} lying on simple wooden bed sleeping with serene face, {TIEN_ONG_BCBD} floating above him in glowing golden mist with finger raised giving sacred guidance, ethereal cyan-gold magical particles floating around the room, mystical dreamlike lighting.",
        # 8 — Body 6: Tiên dạy công thức 2 bánh
        f"Continuing dream sequence: {TIEN_ONG_BCBD} pointing with one hand at floating holographic vision of {BANH_CHUNG} square and {BANH_DAY} round cake side by side, magical golden glow connecting them, swirling stars representing trời đất, {LANG_LIEU} kneeling listening with awe expression, mystical cosmic atmosphere.",
        # 9 — Body 7: Tỉnh dậy chọn nguyên liệu
        f"Daybreak preparation scene: {LANG_LIEU} crouched in rice field at sunrise carefully selecting grains of sticky rice nếp into woven basket, bamboo basket of dong leaves beside him, freshly butchered pork laid on banana leaves nearby, determined focused expression, warm morning golden light, {LANG_QUE_BCBD}.",
        # 10 — Body 8: Gói bánh + giã bánh dày
        f"Cooking workshop scene: {LANG_LIEU} in simple kitchen interior wrapping {BANH_CHUNG} on a wooden table with precise hand movements arranging dong leaves rice mung bean pork in layers, stone mortar with wooden pestle giã nhuyễn cooked sticky rice for {BANH_DAY} beside him, golden afternoon light streaming through window, craftsman concentration.",
        # 11 — Body 9: Hoàng tử khác dâng sơn hào hải vị
        f"Royal banquet hall scene: {HOANG_TU_NHA_GIAU} lined up presenting elaborate dishes - one with whole roasted deer on silver platter, one with platter of live lobsters and crabs, one with bowl of exotic spices and rare delicacies, {VUA_HUNG_BCBD} sitting on throne observing impassively, {COURT_BCBD}, opulent regal lighting.",
        # 12 — Body 10: Lang Liêu dâng bánh + hoàng tử cười khẩy
        f"Court humility scene: {LANG_LIEU} kneeling humbly before {VUA_HUNG_BCBD} on golden throne offering a simple wooden tray with one {BANH_CHUNG} and one {BANH_DAY}, {HOANG_TU_NHA_GIAU} in background covering mouths smirking dismissively, {COURT_BCBD}, dramatic spotlight on Lang Liêu amid sneering elite, golden warm lighting on the modest tray.",
        # 13 — Body 11: Vua truyền ngôi + crowning
        f"Crowning climactic scene: {VUA_HUNG_BCBD} standing from throne placing a golden royal crown on {LANG_LIEU}'s head with proud expression, {BANH_CHUNG} cut showing vivid layers on a small ceremonial table nearby, {HOANG_TU_NHA_GIAU} standing stunned in background mouths agape, warm golden divine lighting illuminating Lang Liêu, {COURT_BCBD}, triumphant climactic mood.",
        # 14 — Moral Tết family gathering
        f"Closing peaceful Tết scene: traditional Vietnamese family gathered around large red glowing fire boiling a giant pot of {BANH_CHUNG} on dark cold winter night, parents children grandparents smiling warmly together, warm amber palette red paper lanterns swaying overhead, oil-painting feel hopeful timeless tradition mood, intergenerational warmth.",
    ],
    "motions": ["static","static","static","pan_right","pan_right","static","static","static","static","static","pan_right","static","static","zoom_out"],
    "caption_hook": "Anh em đã nghe Bánh Chưng Bánh Dày kiểu phim Ratatouille chưa? 🍚🎋 Hoàng tử mồ côi mẹ thắng cuộc thi truyền ngôi chỉ bằng cái bánh quê!",
    "caption_bullets": [
        "Vua Hùng đời 6 mở cuộc thi MasterChef truyền ngôi",
        "22 hoàng tử chen nhau dâng sơn hào hải vị quý hiếm",
        "Lang Liêu con thứ 18 mồ côi mẹ, không có gì để dâng",
        "Giấc mộng tiên ông: trong trời đất không có gì quý bằng hạt gạo",
        "Tự tay gói bánh chưng vuông + bánh dày tròn từ gạo nếp",
        "Vua nếm hài lòng, truyền ngôi ngay cho Lang Liêu",
        "Gốc tích bánh chưng bánh dày Tết Việt Nam"
    ],
    "caption_moral": "Câu chuyện dạy ta: giá trị thực sự không nằm ở xa hoa cầu kỳ, mà ở khả năng trân quý những điều giản dị nhất quanh mình."
}

# ================ BOOK 10: SỰ TÍCH HỒ GƯƠM ================
LE_LOI = _char("Lê Lợi", "young Vietnamese man, heroic uprising leader: navy-blue solid warrior tunic no print over dark streetwear trousers, leather boots, gold chain, undercut black hair, strong determined charismatic face")
LE_LOI_VUA = _char("Lê Lợi as King Lê Thái Tổ", "the same young Vietnamese man now as emperor: golden-yellow royal dragon robe, royal crown, gold chain, undercut black hair, dignified regal face — same person as Lê Lợi warrior")
LE_THAN = _char("Lê Thận", "young Vietnamese fisherman: simple brown solid tunic no print + rolled-up trousers, sandals, weathered honest face, undercut black hair")
RUA_VANG = "giant Golden Turtle Rùa Vàng: enormous ancient turtle with a luminous golden-bronze shell, wise glowing eyes, emerging from lake water, mystical golden aura"
GUOM_TT = "the magic sword Thuận Thiên: a glowing legendary Vietnamese sword, jade-and-gold studded hilt, gleaming steel blade with faint engraved characters, emanating golden cyan magical light"
GIAC_MINH = "Ming dynasty invader soldiers giặc Minh: armored 15th-century Chinese soldiers in dark lacquered armor with red banners, menacing"
NGHIA_QUAN = "Lam Sơn rebel army nghĩa quân: ragtag Vietnamese rebel fighters in simple brown tunics and conical hats, bamboo spears and swords, determined peasant warriors"
RUNG_LAM_SON = "dense misty mountain forest of the Lam Sơn region: tall ancient trees, fog, rugged terrain, hidden rebel camp atmosphere"
LAKE_TA_VONG = "serene lake in the ancient Vietnamese capital: calm green water, a small turtle tower islet, willow trees on the banks, traditional pavilions, peaceful misty atmosphere"

HO_GUOM_BOOK = {
    "slug": "su-tich-ho-guom",
    "title": "Sự Tích Hồ Gươm",
    "story_summary": "Văn Vở Gen Z. Giặc Minh đô hộ, Lê Lợi khởi nghĩa Lam Sơn yếu thế. Đức Long Quân cho mượn gươm thần Thuận Thiên — Lê Thận vớt lưỡi gươm, Lê Lợi tìm chuôi gươm, ráp vừa khít. Nghĩa quân đại thắng đuổi giặc Minh, Lê Lợi lên ngôi. Một năm sau Rùa Vàng đòi gươm, hồ Tả Vọng thành Hồ Hoàn Kiếm. Phiên bản kiểu phim Excalibur (1981).",
    "scripts": [
        # Scene 1 — Hook (1 scene duy nhất)
        "Hôm nay chúng ta sẽ nói về một truyền thuyết gắn liền với trái tim của thủ đô Hà Nội, đó là sự tích Hồ Gươm. Nếu phải so với một bộ phim để anh em dễ hình dung thì tôi xếp nó ngang hàng Excalibur, câu chuyện về một thanh gươm huyền thoại và vị vua được trời chọn. Câu chuyện có giặc Minh đô hộ tàn bạo, có nghĩa quân Lam Sơn khởi nghĩa từ con số không, có thanh gươm thần Thuận Thiên ráp từ hai mảnh ở hai nơi khác nhau. Và có cả màn trả gươm cho Rùa Vàng, giải thích vì sao giữa lòng Hà Nội lại có một cái hồ mang tên Hoàn Kiếm.",
        # Scene 2 — Chương 1: giặc Minh đô hộ
        "Câu chuyện bắt đầu vào đầu thế kỷ mười lăm, khi giặc Minh từ phương Bắc tràn sang đô hộ nước ta. Anh em cứ hình dung kiểu một tập đoàn nước ngoài siêu mạnh nhảy vào thâu tóm toàn bộ thị trường, vơ vét của cải và bóc lột dân ta đến tận xương tủy. Dân chúng khắp nơi sống trong cảnh lầm than, ai dám phản kháng là bị đàn áp dã man không nương tay. Trong bối cảnh ngột ngạt đó, lòng dân ai cũng sục sôi mong có một người đứng lên dẹp loạn, giành lại đất nước.",
        # Scene 3 — Chương 1: Lê Lợi khởi nghĩa Lam Sơn yếu thế
        "Giữa lúc đó, tại vùng đất Lam Sơn xứ Thanh Hóa, có một người tên là Lê Lợi đứng ra dựng cờ khởi nghĩa. Profile của Lê Lợi thì giống một anh founder khởi nghiệp đầy nhiệt huyết nhưng vốn liếng gần như con số không. Nghĩa quân Lam Sơn ngày đầu quân số ít ỏi, vũ khí thô sơ, lương thực thiếu thốn, đúng kiểu một startup non trẻ phải đấu với ông trùm độc quyền của cả ngành. Những trận đầu ra quân, nghĩa quân thua liên tiếp, nhiều phen bị giặc Minh truy đuổi tan tác phải rút sâu vào rừng ẩn náu.",
        # Scene 4 — Chương 2: Long Quân cho mượn gươm + Lê Thận vớt lưỡi gươm
        "Thấy nghĩa quân Lam Sơn nhiều lần thất bại, Đức Long Quân ở dưới thủy cung quyết định ngầm giúp một tay, cho nghĩa quân mượn một thanh gươm thần. Nhưng cách trao gươm thì không hề đơn giản, Long Quân chia thanh gươm làm hai mảnh đặt ở hai nơi cách xa nhau. Ở vùng ven sông có một người đánh cá nghèo tên là Lê Thận, đêm nọ anh quăng lưới kéo lên thì thấy một thanh sắt nặng trịch. Lê Thận bực mình ném đi rồi quăng lưới chỗ khác, nhưng kéo lên vẫn đúng thanh sắt đó, lần thứ ba vẫn vậy khiến anh đứng hình.",
        # Scene 5 — Chương 2: Lê Thận soi đuốc + gia nhập nghĩa quân + gươm sáng
        "Lê Thận lấy làm lạ, đưa thanh sắt lại gần ngọn đuốc soi cho rõ, thì hóa ra đó là một lưỡi gươm sáng loáng. Anh không nghĩ nhiều, đem lưỡi gươm về nhà cất đi như một kỷ vật bình thường. Ít lâu sau, Lê Thận gia nhập nghĩa quân Lam Sơn, chiến đấu gan dạ nên được mọi người quý mến. Một hôm Lê Lợi cùng vài người tùy tùng ghé thăm nhà Lê Thận, vừa bước vào thì lưỡi gươm trong góc nhà bỗng sáng rực lên một cách kỳ lạ, như muốn chào đón chủ nhân thật sự của nó.",
        # Scene 6 — Chương 3: chữ Thuận Thiên + Lê Lợi chạy rừng thấy ánh sáng
        "Lê Lợi tò mò cầm lưỡi gươm lên xem, thì phát hiện trên thân gươm có khắc hai chữ Thuận Thiên, nghĩa là thuận theo ý trời. Lúc đó không ai hiểu rõ ý nghĩa của hai chữ này, mọi người chỉ nghĩ đây là một thanh gươm quý rồi cũng không để tâm lắm. Cho đến một ngày, Lê Lợi bị giặc Minh truy đuổi gắt gao phải một mình chạy trốn vào rừng sâu. Đang lúc hớt hải băng qua rừng, anh chợt thấy một ánh sáng kỳ lạ phát ra từ ngọn cây đa cổ thụ phía trước mặt.",
        # Scene 7 — Chương 3: chuôi gươm + ráp lại vừa khít
        "Lê Lợi trèo lên cây xem thử, thì hóa ra ánh sáng phát ra từ một cái chuôi gươm nạm ngọc lấp lánh tuyệt đẹp. Anh chợt nhớ đến lưỡi gươm khắc chữ Thuận Thiên ở nhà Lê Thận, linh cảm hai thứ này có liên quan đến nhau. Lê Lợi đem chuôi gươm về tra thử vào lưỡi gươm kia, thì kỳ lạ thay hai mảnh khớp vào nhau vừa khít như được đo đúc sẵn cho nhau từ trước. Lê Thận cùng mọi người chứng kiến đều quỳ xuống, nâng gươm dâng cho Lê Lợi và nói rằng đây chính là ý trời giao phó việc cứu nước cho ngài.",
        # Scene 8 — Chương 4: có gươm thần sức mạnh tăng vọt
        "Từ ngày có thanh gươm thần Thuận Thiên trong tay, nhuệ khí của nghĩa quân Lam Sơn lên cao chưa từng thấy. Anh em cứ hình dung như một đội game vừa nhặt được món vũ khí tối thượng, chỉ số sức mạnh tăng vọt lên một đẳng cấp hoàn toàn mới. Lê Lợi cầm gươm xông trận, đi tới đâu quân Minh khiếp vía tới đó, nghĩa quân từ thế bị truy đuổi chuyển sang thế chủ động tấn công. Quân số ngày càng đông, dân chúng khắp nơi nghe tin kéo về xin gia nhập, thanh thế nghĩa quân lớn mạnh như vũ bão.",
        # Scene 9 — Chương 4: combat thắng trận liên tiếp
        "Có gươm thần tiếp sức, nghĩa quân Lam Sơn mở hàng loạt trận combat lớn nhỏ và thắng gần như tuyệt đối. Những trận đánh từng khiến nghĩa quân thua tan tác ngày trước, giờ đây đều xoay chuyển hoàn toàn cục diện. Gươm Thuận Thiên trong tay Lê Lợi như có thần lực, chém tướng phá thành không gì cản nổi. Quân Minh dù đông đảo và trang bị tốt hơn, nhưng trước khí thế của nghĩa quân thì cũng dần thất thế, co cụm phòng thủ rồi tháo chạy khắp nơi.",
        # Scene 10 — Chương 5: đuổi sạch giặc Minh + Lê Lợi lên ngôi
        "Sau nhiều năm chiến đấu bền bỉ, cuối cùng nghĩa quân Lam Sơn cũng quét sạch giặc Minh ra khỏi bờ cõi, giành lại trọn vẹn đất nước. Cuộc khởi nghĩa từ một nhóm nhỏ trong rừng sâu đã làm nên điều tưởng chừng không thể, đánh bại cả một đế chế xâm lược hùng mạnh. Lê Lợi lên ngôi vua, lấy hiệu là Lê Thái Tổ, mở ra một triều đại mới cho nước nhà. Nhân dân khắp nơi mừng vui khôn xiết, sau bao năm khói lửa cuối cùng cũng được sống trong cảnh thái bình thịnh trị.",
        # Scene 11 — Chương 6: một năm sau dạo hồ Tả Vọng
        "Khoảng một năm sau ngày đất nước thái bình, vào một buổi đẹp trời, vua Lê Thái Tổ cưỡi thuyền rồng dạo chơi trên hồ Tả Vọng ở giữa kinh thành. Lúc này chiến tranh đã lùi xa, nhà vua thong dong ngắm cảnh non nước hữu tình, trong lòng nhẹ nhõm thư thái. Thanh gươm thần Thuận Thiên vẫn luôn được nhà vua mang theo bên mình như một báu vật gắn liền với cả cuộc khởi nghĩa. Nhưng nhà vua đâu ngờ rằng, đây chính là ngày thanh gươm sắp hoàn thành sứ mệnh của nó.",
        # Scene 12 — Final: Rùa Vàng đòi gươm (ICONIC verbatim)
        "Bỗng nhiên giữa mặt hồ, một con rùa vàng khổng lồ từ từ nổi lên, bơi lại gần thuyền rồng của nhà vua. Cả đoàn tùy tùng còn đang đứng hình ngơ ngác, thì Rùa Vàng cất tiếng nói rõ ràng như người: xin bệ hạ hoàn gươm lại cho Long Quân. Lúc này Lê Lợi mới hiểu ra, thanh gươm thần năm xưa là do Đức Long Quân cho nghĩa quân mượn để đánh giặc cứu nước. Nay giặc đã tan và đất nước thái bình, thanh gươm phải được trả lại cho chủ cũ. Nhà vua liền nâng gươm bằng hai tay, trang trọng trao trả cho Rùa Vàng.",
        # Scene 13 — Moral
        "Rùa Vàng ngậm lấy thanh gươm rồi từ từ lặn sâu xuống đáy hồ, mang theo ánh hào quang cuối cùng của một thời khói lửa. Từ đó, hồ Tả Vọng được đổi tên thành hồ Hoàn Kiếm, nghĩa là hồ trả gươm, cái tên còn lưu giữ đến tận ngày nay. Câu chuyện sự tích Hồ Gươm dạy ta rằng sức mạnh dù lớn đến đâu cũng chỉ là thứ được trao gửi tạm thời, quan trọng là dùng nó đúng lúc khi đất nước cần và biết buông bỏ khi thái bình lập lại. Mỗi lần ngắm hồ Gươm xanh biếc giữa lòng Hà Nội, ta lại nhớ về bài học của lòng biết ơn và tinh thần yêu chuộng hòa bình của dân tộc Việt Nam.",
    ],
    "image_prompts": [
        # 1 — Hook movie poster Excalibur split
        f"Movie-poster composition: {LE_LOI} on LEFT half holding the glowing {GUOM_TT} raised heroically, {LAKE_TA_VONG} with {RUA_VANG} emerging on RIGHT half, dramatic split lighting epic legendary, fairy-tale poster framing.",
        # 2 — Chương 1: giặc Minh đô hộ
        f"Oppression scene: {GIAC_MINH} marching through a ransacked Vietnamese village, frightened peasants bowing low, smoke rising and red banners, dark oppressive mood, 15th century setting.",
        # 3 — Chương 1: Lê Lợi khởi nghĩa Lam Sơn
        f"Rebel camp scene: {LE_LOI} standing before a small gathering of {NGHIA_QUAN} raising a banner in {RUNG_LAM_SON}, modest campfire, determined underdog mood, misty forest.",
        # 4 — Chương 2: Lê Thận vớt lưỡi gươm
        f"Night fishing scene: {LE_THAN} in a small wooden boat on a moonlit river, pulling up his fishing net to find a mysterious heavy glowing sword blade, lantern light, astonished expression, mystical atmosphere.",
        # 5 — Chương 2: Lê Thận soi đuốc + gươm sáng khi Lê Lợi đến
        f"Humble hut interior: {LE_THAN} holding a sword blade near a flaming torch revealing it gleaming, {LE_LOI} entering the doorway, the {GUOM_TT} blade glowing brightly cyan-gold as if greeting him, dramatic warm light.",
        # 6 — Chương 3: Lê Lợi chạy rừng thấy ánh sáng
        f"Forest chase scene: {LE_LOI} running alone through dense {RUNG_LAM_SON} glancing back warily, ahead a mysterious golden light glowing from the top of an ancient banyan tree, dramatic dappled moonlight, suspense.",
        # 7 — Chương 3: ráp gươm vừa khít
        f"Pivotal scene: {LE_LOI} fitting a jewel-studded sword hilt onto a blade, the two halves of {GUOM_TT} joining together with a burst of golden cyan magical light, {LE_THAN} and {NGHIA_QUAN} kneeling around in awe, epic mystical moment.",
        # 8 — Chương 4: có gươm thần sức mạnh tăng vọt
        f"Empowered rebel scene: {LE_LOI} holding the radiant {GUOM_TT} aloft before a large crowd of {NGHIA_QUAN} cheering, banners raised high, sunrise golden light, triumphant rising-power mood.",
        # 9 — Chương 4: combat thắng trận
        f"Epic battle scene: {LE_LOI} charging with the glowing {GUOM_TT} leading {NGHIA_QUAN} against {GIAC_MINH}, dynamic combat, dust and banners, low-angle hero shot, decisive victory mood.",
        # 10 — Chương 5: Lê Lợi lên ngôi
        f"Coronation scene: {LE_LOI_VUA} seated on a golden throne, veteran {NGHIA_QUAN} fighters and courtiers celebrating around, warm golden palace lighting, triumphant peaceful mood.",
        # 11 — Chương 6: dạo hồ Tả Vọng
        f"Serene scene: {LE_LOI_VUA} standing on an ornate dragon boat gliding across {LAKE_TA_VONG}, calm green water, willow trees, the sheathed {GUOM_TT} at his side, peaceful misty morning, golden light.",
        # 12 — Final: Rùa Vàng đòi gươm
        f"Iconic legendary scene: {RUA_VANG} emerging majestically from the lake water beside the dragon boat, {LE_LOI_VUA} standing and lifting the glowing {GUOM_TT} with both hands to return it, attendants stunned, {LAKE_TA_VONG}, dramatic mystical golden light.",
        # 13 — Moral: Rùa Vàng lặn + hồ Hoàn Kiếm
        f"Closing peaceful scene: {RUA_VANG} diving back into {LAKE_TA_VONG} holding the {GUOM_TT}, ripples and a last golden glow on the calm green water, the iconic turtle tower islet, willow trees, contemplative oil-painting feel, hopeful timeless mood, no other characters.",
    ],
    "motions": ["static","static","pan_right","static","static","static","static","static","zoom_out","pan_right","static","pan_right","static","zoom_out"],
    "caption_hook": "Anh em đã nghe Sự Tích Hồ Gươm kiểu phim Excalibur chưa? ⚔️🐢 Gươm thần Thuận Thiên ráp từ 2 mảnh, đánh tan giặc Minh rồi trả lại cho Rùa Vàng!",
    "caption_bullets": [
        "Giặc Minh đô hộ, dân ta sống cảnh lầm than",
        "Lê Lợi dựng cờ khởi nghĩa Lam Sơn từ con số không",
        "Lê Thận vớt được lưỡi gươm khắc chữ Thuận Thiên 3 lần",
        "Lê Lợi tìm thấy chuôi gươm nạm ngọc trên cây đa",
        "Ráp 2 mảnh vừa khít — gươm thần Thuận Thiên hoàn chỉnh",
        "Nghĩa quân đại thắng, đuổi sạch giặc Minh, Lê Lợi lên ngôi vua",
        "Rùa Vàng đòi gươm — hồ Tả Vọng đổi tên thành Hồ Hoàn Kiếm"
    ],
    "caption_moral": "Câu chuyện dạy ta: sức mạnh chỉ là thứ được trao gửi tạm thời — dùng đúng lúc khi đất nước cần, và biết buông bỏ khi thái bình lập lại."
}

# ================ EXPORT ================
BOOKS = {
    "thach-sanh": THACH_SANH_BOOK,
    "so-dua": SO_DUA_BOOK,
    "cay-tre-tram-dot": CAY_TRE_BOOK,
    "an-khe-tra-vang": AN_KHE_BOOK,
    "son-tinh-thuy-tinh": SON_TINH_BOOK,
    "tam-cam": TAM_CAM_BOOK,
    "mai-an-tiem": MAI_AN_TIEM_BOOK,
    "chu-cuoi-cung-trang": CHU_CUOI_BOOK,
    "banh-chung-banh-day": BANH_CHUNG_BOOK,
    "su-tich-ho-guom": HO_GUOM_BOOK,
}
