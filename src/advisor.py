def generate_orchard_advisories(analysis: dict) -> list[dict]:
    advisories = []

    temp_diff = analysis["temp_diff"]
    rain_ratio = analysis["rain_ratio"]
    current_dtr = analysis["current_dtr"]

    if temp_diff >= 2.0:
        advisories.append({
            "level": "warning",
            "category": "月均溫偏高（暖冬／熱逆境）",
            "title": "花芽分化與蒸散加速預警",
            "action": "本月均溫高於歷年同期 2°C 以上，易導致果樹休眠不足或花期紊亂；建議加強樹冠微噴霧降溫，並適時補充鈣、硼葉面肥以維持著果率。",
        })
    elif temp_diff <= -2.0:
        advisories.append({
            "level": "danger",
            "category": "月均溫偏低（寒害風險）",
            "title": "低溫寒害防護行動",
            "action": "本月均溫顯著低於歷年同期，幼果與新梢易受寒害；建議於迎風面架設防風網、進行果實套袋保溫，並於寒流前夕提前灌水穩定地溫。",
        })

    if rain_ratio >= 150.0:
        advisories.append({
            "level": "danger",
            "category": "累積雨量異常偏高（豪雨／高濕）",
            "title": "排水疏通與真菌病害預防",
            "action": "當月累積雨量已達同期 150% 以上，土壤含水過高易引發根系缺氧、裂果及炭疽病／露疫病；請立即巡視果園排水溝清淤，並於雨停空檔執行預防性噴藥。",
        })
    elif rain_ratio <= 50.0:
        advisories.append({
            "level": "warning",
            "category": "累積雨量嚴重偏少（乾旱預警）",
            "title": "節水滴灌與地表覆蓋保濕",
            "action": "當月累積雨量不及歷年同期一半，果實膨大期恐受缺水影響；建議啟動分區滴灌補水，並在樹盤覆蓋稻草或雜草抑制土壤水分散失。",
        })

    if current_dtr >= 12.0:
        advisories.append({
            "level": "info",
            "category": "日夜溫差顯著（DTR ≥ 12°C）",
            "title": "果實轉色糖度累積期與裂果防範",
            "action": "目前日夜溫差大，極有利於果實糖度累積與表皮轉色；惟白天升溫快、夜間降溫劇烈，需保持土壤濕度穩定，避免水分劇烈波動造成生理裂果。",
        })

    if not advisories:
        advisories.append({
            "level": "success",
            "category": "氣候指標穩定",
            "title": "維持常規果園田間管理",
            "action": "目前月均溫、累積雨量與日夜溫差皆落於歷年同期正常區間，適合依既定排程進行修剪、疏果與常規肥培管理。",
        })

    return advisories