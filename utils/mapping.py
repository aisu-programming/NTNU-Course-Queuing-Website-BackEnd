# -*- coding: UTF-8 -*-

""" Department """
department_text  = [ "通識", "共同科", "師培學院", "普通體育", "全人中心", "教育學院", "教育系", "教育碩", "教育博", "心輔系", "心輔碩", "心輔博", "社教系", "社教碩", "社教博", "衛教系", "衛教碩", "衛教博", "人發系", "人發碩", "人發博", "公領系", "公領碩", "公領博", "資訊碩", "資訊博", "特教系", "特教碩", "特教博", "學習科學學位學程", "圖資碩", "圖資博", "教政碩", "復諮碩", "教院不分系", "課教碩", "課教博", "文學院", "國文系", "國文碩", "英語系", "英語碩", "英語博", "英語輔", "歷史系", "歷史碩", "歷史輔", "地理系", "地理碩", "地理博", "翻譯碩", "翻譯博", "臺文系", "臺文碩", "臺史碩", "數學系", "數學碩", "物理系", "物理碩", "化學系", "化學碩", "化學博", "生科系", "生科碩", "生科博", "地科系", "地科碩", "地科博", "科教碩", "科教博", "環教碩", "環教博", "資工系", "資工碩", "生物多樣學位學程", "營養科學學位學程", "營養碩", "生醫碩", "藝術學院", "美術系", "美術碩", "美術博", "藝史碩", "設計系", "設計碩", "設計博", "科技學院", "工教系", "工教碩", "工教博", "科技系", "科技碩", "科技博", "圖傳系", "圖傳碩", "機電系", "機電碩", "機電博", "電機系", "電機碩", "車能學位學程", "光電工程學位學程", "光電碩", "運休學院", "體育系", "體育碩", "體育博", "休旅碩", "休旅博", "競技系", "競技碩", "國社學院", "歐文碩", "東亞系", "東亞碩", "東亞博", "華語系", "華語碩", "華語博", "人資碩", "政治碩", "大傳碩", "社工碩", "音樂系", "音樂碩", "音樂博", "民音碩", "表演學位學程", "表演碩", "管理學院", "管理碩", "全營碩", "企管系", "戶外探索領導學程", "科學計算學程", "太陽能源與工程學程", "文物保存修復學分學程", "運動傷害防護學程", "國際教師學程-華語文", "國際教師學程-數學", "國際教師學程-物理", "資訊科技應用學程", "人工智慧技術與應用學程", "PASSION偏鄉教育學程", "基礎管理學程", "財金學程", "影音藝術學程", "環境監測學程", "榮譽英語學程", "歐洲文化學程", "文學創作學程", "日語學程", "高齡學程", "區域學程", "空間學程", "學校心理學學程", "社會與傳播學程", "大數據學程", "室內設計學程", "韓語學程", "社團領導學程", "國際文化學程", "兒童雙語學程", "原民教育學程", "大師創業學程", "金牌書院", "哲學學程", "藝術產業學程", "國際教師學程-國際" ]  # "所有系所"

department_code = [ "GU", "CU", "EU", "PE", "VS", "E", "EU00", "EM00", "ED00", "EU01", "EM01", "ED01", "EU02", "EM02", "ED02", "EU05", "EM05", "ED05", "EU06", "EM06", "ED06", "EU07", "EM07", "ED07", "EM08", "ED08", "EU09", "EM09", "ED09", "EU11", "EM15", "ED15", "EM16", "EM17", "EU13", "EM03", "ED03", "L", "LU20", "LM20", "LU21", "LM21", "LD21", "SA21", "LU22", "LM22", "SA22", "LU23", "LM23", "LD23", "LM25", "LD25", "LU26", "LM26", "LM27", "SU40", "SM40", "SU41", "SM41", "SU42", "SM42", "SD42", "SU43", "SM43", "SD43", "SU44", "SM44", "SD44", "SM45", "SD45", "SM46", "SD46", "SU47", "SM47", "SD50", "SU51", "SM51", "SM52", "T", "TU60", "TM60", "TD60", "TM67", "TU68", "TM68", "TD68", "H", "HU70", "HM70", "HD70", "HU71", "HM71", "HD71", "HU72", "HM72", "HU73", "HM73", "HD73", "HU75", "HM75", "HU76", "HU77", "HM77", "A", "AU30", "AM30", "AD30", "AM31", "AD31", "AU32", "AM32", "I", "IM82", "IU83", "IM83", "ID83", "IU84", "IM84", "ID84", "IM86", "IM87", "IM88", "IM89", "MU90", "MM90", "MD90", "MM91", "MU92", "MM92", "O", "OM55", "OM56", "OU57", "ZU66", "ZU67", "ZU68", "ZU69", "ZU73", "ZU74", "ZU75", "ZU76", "ZU77", "ZU78", "ZU79", "ZU83", "ZU84", "ZU88", "ZU89", "ZU92", "ZU93", "ZU94", "ZU97", "ZU98", "ZU9A", "ZU9B", "ZU9C", "ZU9E", "ZU9K", "ZU9O", "ZU9P", "ZU9Q", "ZU9R", "ZU9T", "ZU9U", "ZU9V", "ZU9W", "ZU9X", "ZU9Y", "ZU9Z" ]  # ""

department_text2code = dict(zip(department_text, department_code))
department_code2text = dict(zip(department_code, department_text))
department_code2id   = dict(zip(department_code, list(range(len(department_code)))))



""" Domain """
domain_106_text = [ "語言與文學", "藝術與美感", "哲學思維與道德推理", "公民素養與社會探究", "歷史與文化", "數學與邏輯思維", "科學與生命", "第二外語", "生活技能", "自主學習" ]  # "請選擇", "所有通識"
domain_106_code = [ "00UG", "01UG", "02UG", "03UG", "04UG", "05UG", "06UG", "07UG", "08UG", "09UG" ]  # "0", "all"
# domain_106_text2code = dict(zip(domain_106_text, domain_106_code))
domain_106_code2text = dict(zip(domain_106_code, domain_106_text))
# domain_106_code2id   = dict(zip(domain_106_code, list(range(len(domain_106_code)))))

domain_109_text = [ "人文藝術", "社會科學", "自然科學", "邏輯運算", "學院共同課程", "跨域專業探索課程", "大學入門", "專題探究", "MOOCs" ]  # "請選擇", "所有通識"
domain_109_code = [ "A1UG", "A2UG", "A3UG", "A4UG", "B1UG", "B2UG", "B3UG", "C1UG", "C2UG" ]  # "0", "all"
# domain_109_text2code = dict(zip(domain_109_text, domain_109_code))
domain_109_code2text = dict(zip(domain_109_code, domain_109_text))
# domain_109_code2id   = dict(zip(domain_109_code, list(range(len(domain_109_code)))))