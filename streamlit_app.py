# حساب حصة الإنزيمات مسبقاً
auto_added_enzymes = {}
if main_sector in ["الأبقار وسلالاتها", "الماعز وسلالاته"] and final_target_cp > 15: # مثال لشرط منظم
    auto_added_enzymes["بيكربونات الصوديوم (الصودا)"] = 0.75
if main_sector == "الطيور والسمان":
    auto_added_enzymes["إنزيم الفايتيز الزامي (Phytase Super-D)"] = 0.05

total_enz_pct = sum(auto_added_enzymes.values())

# المتبقي الفعلي بعد الإضافات الثابتة والإنزيمات
net_available = 100.0 - used_fixed_pct - total_enz_pct

# توزيع مرن دون فرض أرقام صلبة تسبب نسباً سالبة
grain_share = net_available * 0.65  # تخصيص 65% من الصافي للظاقة
leftover_for_others = net_available - grain_share

# توزيع الحصص
for x in grains_ingredients: 
    formula_results[x] = grain_share / len(grains_ingredients)
for x in protein_ingredients: 
    formula_results[x] = leftover_for_others / len(protein_ingredients)

# دمج الإنزيمات لضمان مجموع 100% تماماً
for enz_name, enz_pct in auto_added_enzymes.items(): 
    formula_results[enz_name] = enz_pct
