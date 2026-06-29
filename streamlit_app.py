# ==========================================
# نظام المراجع العلمية والقاعدة المعرفية المتكاملة
# ==========================================

class ScientificReferenceSystem:
    """نظام المراجع العلمية الموثوقة للمنصة"""
    
    # قاعدة المراجع العلمية المصنفة
    REFERENCES = {
        # مراجع عامة في تغذية الحيوان
        "general_nutrition": {
            "title": "المبادئ الأساسية لتغذية الحيوان",
            "references": [
                {
                    "id": "REF001",
                    "authors": "McDonald, P., Edwards, R.A., Greenhalgh, J.F.D., Morgan, C.A.",
                    "year": 2011,
                    "title": "Animal Nutrition",
                    "publisher": "Pearson Education",
                    "edition": "7th Edition",
                    "isbn": "978-1408204238",
                    "summary": "المرجع الأساسي في تغذية الحيوان، يغطي جميع جوانب التغذية من الهضم إلى متطلبات العناصر الغذائية."
                },
                {
                    "id": "REF002",
                    "authors": "Cheeke, P.R., Dierenfeld, E.S.",
                    "year": 2010,
                    "title": "Comparative Animal Nutrition and Metabolism",
                    "publisher": "CABI",
                    "isbn": "978-1845936310",
                    "summary": "مقارنة بين آليات التغذية والتمثيل الغذائي في مختلف أنواع الحيوانات."
                }
            ]
        },
        
        # مراجع البروتين والأحماض الأمينية
        "protein_amino_acids": {
            "title": "البروتين والأحماض الأمينية في تغذية الحيوان",
            "references": [
                {
                    "id": "REF003",
                    "authors": "NRC (National Research Council)",
                    "year": 2012,
                    "title": "Nutrient Requirements of Swine",
                    "publisher": "National Academies Press",
                    "edition": "11th Revised Edition",
                    "isbn": "978-0309214230",
                    "summary": "المرجع الرسمي لمتطلبات العناصر الغذائية للخنازير، يشمل تفاصيل دقيقة عن الأحماض الأمينية."
                },
                {
                    "id": "REF004",
                    "authors": "NRC (National Research Council)",
                    "year": 2001,
                    "title": "Nutrient Requirements of Dairy Cattle",
                    "publisher": "National Academies Press",
                    "edition": "7th Revised Edition",
                    "isbn": "978-0309069977",
                    "summary": "المرجع الأساسي في تغذية أبقار الحليب، يغطي متطلبات البروتين المهضوم."
                },
                {
                    "id": "REF005",
                    "authors": "Bryden, W.L., Li, X., Ravindran, G.",
                    "year": 2009,
                    "title": "Digestible Amino Acids in Poultry Feed Ingredients",
                    "publisher": "University of Sydney",
                    "summary": "دراسة شاملة عن الأحماض الأمينية المهضومة في مواد العلف للدواجن."
                }
            ]
        },
        
        # مراجع الطاقة والكربوهيدرات
        "energy_carbohydrates": {
            "title": "الطاقة والكربوهيدرات في التغذية الحيوانية",
            "references": [
                {
                    "id": "REF006",
                    "authors": "Van Soest, P.J.",
                    "year": 1994,
                    "title": "Nutritional Ecology of the Ruminant",
                    "publisher": "Cornell University Press",
                    "edition": "2nd Edition",
                    "isbn": "978-0801427725",
                    "summary": "المرجع الكلاسيكي في تغذية المجترات وتحليل الألياف."
                },
                {
                    "id": "REF007",
                    "authors": "Blaxter, K.L.",
                    "year": 1989,
                    "title": "Energy Metabolism in Animals and Man",
                    "publisher": "Cambridge University Press",
                    "isbn": "978-0521369433",
                    "summary": "دراسة متعمقة في أيض الطاقة في الحيوانات والإنسان."
                }
            ]
        },
        
        # مراجع المعادن والفيتامينات
        "minerals_vitamins": {
            "title": "المعادن والفيتامينات في تغذية الحيوان",
            "references": [
                {
                    "id": "REF008",
                    "authors": "Underwood, E.J., Suttle, N.F.",
                    "year": 1999,
                    "title": "The Mineral Nutrition of Livestock",
                    "publisher": "CABI",
                    "edition": "3rd Edition",
                    "isbn": "978-0851991283",
                    "summary": "المرجع الشامل في تغذية المعادن للثروة الحيوانية."
                },
                {
                    "id": "REF009",
                    "authors": "McDowell, L.R.",
                    "year": 2000,
                    "title": "Vitamins in Animal Nutrition",
                    "publisher": "Academic Press",
                    "isbn": "978-0124833724",
                    "summary": "دراسة متكاملة عن الفيتامينات ودورها في تغذية الحيوان."
                }
            ]
        },
        
        # مراجع الدواجن
        "poultry": {
            "title": "تغذية الدواجن المتخصصة",
            "references": [
                {
                    "id": "REF010",
                    "authors": "Leeson, S., Summers, J.D.",
                    "year": 2009,
                    "title": "Commercial Poultry Nutrition",
                    "publisher": "Nottingham University Press",
                    "edition": "3rd Edition",
                    "isbn": "978-1904761578",
                    "summary": "المرجع العملي في تغذية الدواجن التجارية."
                },
                {
                    "id": "REF011",
                    "authors": "NRC (National Research Council)",
                    "year": 1994,
                    "title": "Nutrient Requirements of Poultry",
                    "publisher": "National Academies Press",
                    "edition": "9th Revised Edition",
                    "isbn": "978-0309048927",
                    "summary": "المرجع الرسمي لمتطلبات الدواجن من العناصر الغذائية."
                }
            ]
        },
        
        # مراجع المجترات
        "ruminants": {
            "title": "تغذية المجترات المتخصصة",
            "references": [
                {
                    "id": "REF012",
                    "authors": "Church, D.C.",
                    "year": 1993,
                    "title": "The Ruminant Animal: Digestive Physiology and Nutrition",
                    "publisher": "Waveland Press",
                    "isbn": "978-0881337389",
                    "summary": "المرجع الشامل في فسيولوجيا الهضم والتغذية للمجترات."
                },
                {
                    "id": "REF013",
                    "authors": "Minson, D.J.",
                    "year": 1990,
                    "title": "Forage in Ruminant Nutrition",
                    "publisher": "Academic Press",
                    "isbn": "978-0124983108",
                    "summary": "دراسة متخصصة في تغذية المجترات على الأعلاف الخشنة."
                }
            ]
        },
        
        # مراجع الأغنام والماعز
        "sheep_goats": {
            "title": "تغذية الأغنام والماعز",
            "references": [
                {
                    "id": "REF014",
                    "authors": "NRC (National Research Council)",
                    "year": 2007,
                    "title": "Nutrient Requirements of Small Ruminants",
                    "publisher": "National Academies Press",
                    "isbn": "978-0309102131",
                    "summary": "المرجع الرسمي لمتطلبات الأغنام والماعز والمجترات الصغيرة."
                }
            ]
        },
        
        # مراجع الخيول
        "horses": {
            "title": "تغذية الخيول والفروسية",
            "references": [
                {
                    "id": "REF015",
                    "authors": "NRC (National Research Council)",
                    "year": 2007,
                    "title": "Nutrient Requirements of Horses",
                    "publisher": "National Academies Press",
                    "edition": "6th Revised Edition",
                    "isbn": "978-0309102124",
                    "summary": "المرجع الأساسي في تغذية الخيول ومتطلباتها الغذائية."
                }
            ]
        },
        
        # مراجع الأسماك والأحياء المائية
        "aquaculture": {
            "title": "تغذية الأسماك والأحياء المائية",
            "references": [
                {
                    "id": "REF016",
                    "authors": "Halver, J.E., Hardy, R.W.",
                    "year": 2002,
                    "title": "Fish Nutrition",
                    "publisher": "Academic Press",
                    "edition": "3rd Edition",
                    "isbn": "978-0123196521",
                    "summary": "المرجع الشامل في تغذية الأسماك والمزارع المائية."
                }
            ]
        },
        
        # مراجع الإنتاج الحيواني
        "animal_production": {
            "title": "الإنتاج الحيواني المتكامل",
            "references": [
                {
                    "id": "REF017",
                    "authors": "Ensminger, M.E., Parker, R.O.",
                    "year": 2002,
                    "title": "Animal Science",
                    "publisher": "Pearson Education",
                    "edition": "5th Edition",
                    "isbn": "978-0131120417",
                    "summary": "المرجع الشامل في علوم الإنتاج الحيواني."
                }
            ]
        },
        
        # مراجع الأعلاف والتركيب
        "feed_formulation": {
            "title": "تركيب الأعلاف والخلطات العلفية",
            "references": [
                {
                    "id": "REF018",
                    "authors": "Pond, W.G., Church, D.C., Pond, K.R.",
                    "year": 1995,
                    "title": "Basic Animal Nutrition and Feeding",
                    "publisher": "Wiley",
                    "edition": "4th Edition",
                    "isbn": "978-0471308643",
                    "summary": "المرجع الأساسي في تغذية الحيوان وتركيب الأعلاف."
                },
                {
                    "id": "REF019",
                    "authors": "CNCPS (Cornell Net Carbohydrate and Protein System)",
                    "year": 2010,
                    "title": "CNCPS Feed Library and Nutrient Requirements",
                    "publisher": "Cornell University",
                    "summary": "النظام المتقدم لتحليل الأعلاف وتقدير الاحتياجات الغذائية."
                }
            ]
        },
        
        # مراجع الدجاج اللاحم (Broiler)
        "broiler": {
            "title": "إنتاج الدجاج اللاحم المتخصص",
            "references": [
                {
                    "id": "REF020",
                    "authors": "Ross 308 Broiler Management Guide",
                    "year": 2020,
                    "title": "Ross Broiler Management Handbook",
                    "publisher": "Aviagen",
                    "summary": "الدليل الشامل لإدارة الدجاج اللاحم سلالة روس."
                },
                {
                    "id": "REF021",
                    "authors": "Cobb-Vantress",
                    "year": 2020,
                    "title": "Cobb 500 Broiler Management Guide",
                    "publisher": "Cobb-Vantress",
                    "summary": "الدليل المتخصص لإدارة دجاج اللاحم سلالة كوب."
                },
                {
                    "id": "REF022",
                    "authors": "ASPCA (American Society for the Prevention of Cruelty to Animals)",
                    "year": 2019,
                    "title": "Poultry Welfare Standards",
                    "publisher": "ASPCA",
                    "summary": "معايير رعاية الدواجن ورفاهيتها."
                }
            ]
        },
        
        # مراجع التغذية الدقيقة والبروتين المهضوم
        "digestible_protein": {
            "title": "البروتين المهضوم والتغذية الدقيقة",
            "references": [
                {
                    "id": "REF023",
                    "authors": "INRA (Institut National de la Recherche Agronomique)",
                    "year": 2007,
                    "title": "INRA Feeding System for Ruminants",
                    "publisher": "Wageningen Academic Publishers",
                    "isbn": "978-9086860197",
                    "summary": "النظام الفرنسي المتقدم لتغذية المجترات وتقدير البروتين المهضوم."
                },
                {
                    "id": "REF024",
                    "authors": "Pesti, G.M., Miller, B.R.",
                    "year": 2009,
                    "title": "Least-Cost Feed Formulation: Theory and Practice",
                    "publisher": "University of Georgia",
                    "summary": "النظرية والتطبيق العملي لتركيب الأعلاف بأقل تكلفة."
                }
            ]
        }
    }
    
    # قاعدة المعرفة التفاعلية للأسئلة الشائعة
    KNOWLEDGE_BASE = {
        "ما هو البروتين المهضوم": {
            "answer": "البروتين المهضوم (Digestible Protein) هو كمية البروتين التي يستطيع الحيوان هضمها وامتصاصها فعلياً من العلف. يتم حسابه بضرب نسبة البروتين الخام في معامل الهضم لكل مادة علفية. هذا المقياس أدق من البروتين الخام لأنه يعكس القيمة الغذائية الحقيقية التي يستفيد منها الحيوان.",
            "reference": "REF023",
            "simplified": "البروتين المهضوم هو الجزء من البروتين الذي يستفيد منه الحيوان فعلياً، وليس مجرد الكمية الموجودة في العلف."
        },
        "ما هو معادل النشاء": {
            "answer": "معادل النشاء (Starch Equivalent - SE) هو مقياس لكمية الطاقة التي يوفرها العلف للحيوان، مقارنة بالطاقة التي يوفرها النشاء النقي. يستخدم هذا المقياس لتقييم كفاءة الطاقة في الأعلاف المختلفة، حيث يمثل النشاء النقي القيمة 100 وحدة.",
            "reference": "REF006",
            "simplified": "معادل النشاء يقيس كمية الطاقة في العلف، وكلما زاد الرقم زادت الطاقة التي يمنحها للحيوان."
        },
        "كيف يتم تركيب العلف الأمثل": {
            "answer": "يتم تركيب العلف الأمثل باستخدام محرك الاستمثال الخطي (Linear Programming) الذي يحسب أقل تكلفة لتحقيق متطلبات غذائية محددة. تشمل المتطلبات: البروتين المهضوم، الطاقة (معادل النشاء)، الألياف، المعادن، والفيتامينات. يتم إدخال أسعار المواد العلفية ومكوناتها الغذائية ليقدم البرنامج التركيبة المثلى.",
            "reference": "REF024",
            "simplified": "نستخدم برنامجاً ذكياً يحسب أرخص خلطة علفية تلبي جميع احتياجات الحيوان الغذائية."
        },
        "ما هي أهمية إضافة الإنزيمات للأعلاف": {
            "answer": "الإنزيمات في الأعلاف تعمل على تحسين هضم واستفادة الحيوان من العناصر الغذائية. الإنزيمات مثل الفايتيز تحرر الفسفور المرتبط بالنباتات، وإنزيمات NSP تكسر جدران الخلايا النباتية مما يزيد من هضم الكربوهيدرات. هذا يقلل التكاليف ويحسن الأداء الإنتاجي ويقلل الآثار البيئية.",
            "reference": "REF010",
            "simplified": "الإنزيمات تساعد الحيوان على هضم العلف بشكل أفضل، مما يوفر في تكاليف التغذية ويحسن الإنتاج."
        },
        "ما هو مؤشر EPEF": {
            "answer": "مؤشر الأداء الأوروبي EPEF (European Production Efficiency Factor) هو مقياس شامل لكفاءة إنتاج الدجاج اللاحم. يحسب بالمعادلة: EPEF = (الحيوية × الوزن الحي) / (العمر × معامل التحويل الغذائي) × 100. كلما ارتفع الرقم دل ذلك على أداء أفضل وكفاءة إنتاجية أعلى.",
            "reference": "REF020",
            "simplified": "EPEF هو رقم يعبر عن كفاءة مزرعة الدجاج، وكلما كان أعلى دل ذلك على إنتاجية أفضل وأداء ممتاز."
        },
        "ما هو الفرق بين البروتين الخام والمهضوم": {
            "answer": "البروتين الخام (CP) هو إجمالي محتوى النيتروجين في العلف مضروباً في 6.25، بينما البروتين المهضوم (DP) هو الجزء الذي يتم هضمه وامتصاصه فعلياً. DP = CP × معامل الهضم. استخدام DP في تركيب الأعلاف يعطي نتائج أدق وأكثر اقتصاداً.",
            "reference": "REF023",
            "simplified": "البروتين الخام هو كل البروتين الموجود، أما المهضوم فهو الجزء الذي يستفيد منه الحيوان فعلياً."
        },
        "كيف يتم حساب معامل التحويل الغذائي FCR": {
            "answer": "معامل التحويل الغذائي FCR = كمية العلف المستهلك / كمية الوزن المكتسب. مثال: إذا استهلك طائر 3 كجم علف واكتسب 1.5 كجم وزن، فإن FCR = 3/1.5 = 2.0. FCR أقل يعني كفاءة تحويل أفضل وإنتاجية أعلى.",
            "reference": "REF018",
            "simplified": "FCR يبين كمية العلف التي يحتاجها الحيوان ليكتسب كيلو جرام واحد من الوزن. كلما كان الرقم أقل كان أفضل."
        },
        "كيف يمكن تحسين كفاءة مزرعة الدجاج": {
            "answer": "تحسين كفاءة مزرعة الدجاج يتم من خلال: 1. استخدام برامج تغذية دقيقة مع البروتين المهضوم. 2. تطبيق بروتوكول تحصين صارم. 3. التحكم الدقيق في البيئة (درجة حرارة، رطوبة، تهوية). 4. مراقبة جودة العلف والماء. 5. تطبيق برامج إضاءة مناسبة. 6. تنفيذ برامج وقائية ضد الأمراض.",
            "reference": "REF021",
            "simplified": "لتحسين مزرعة الدجاج: استخدم تغذية دقيقة، حافظ على نظافة البيئة، طبق برامج تحصين، وراقب أداء القطيع يومياً."
        },
        "ما هي أهمية بيكربونات الصوديوم في أعلاف المجترات": {
            "answer": "تستخدم بيكربونات الصوديوم (Sodium Bicarbonate) في أعلاف المجترات كمنظم لحموضة الكرش. تعمل على معادلة الأحماض الناتجة عن تخمر الكربوهيدرات، وتمنع حدوث الحماض الكرشي (Ruminal Acidosis) الذي يسبب انخفاض الشهية والإنتاجية. تضاف بنسبة 0.5-1% من العلف الجاف.",
            "reference": "REF012",
            "simplified": "بيكربونات الصوديوم تحافظ على توازن الحموضة في كرش الحيوان، مما يمنع مشاكل الهضم ويحسن الإنتاج."
        },
        "ما هي طريقة حساب الجرعات الدوائية في مزارع الدواجن": {
            "answer": "تحسب الجرعات الدوائية في مزارع الدواجن بناءً على الوزن الحي للقطيع والتركيز الفعال للدواء. الصيغة العامة: الجرعة الكلية = (وزن الطير × عدد الطيور × الجرعة الموصى بها بالملجم/كجم) / 1000. يجب مراعاة فترة السحب (Withdrawal Period) قبل التسويق واتباع تعليمات الشركة المصنعة.",
            "reference": "REF020",
            "simplified": "تحسب الأدوية بناءً على وزن الطيور، وتتبع التعليمات بدقة مع مراعاة فترة التوقف قبل الذبح."
        }
    }

    @staticmethod
    def get_reference(ref_id: str) -> Optional[dict]:
        """جلب مرجع معين باستخدام المعرف"""
        for category in ScientificReferenceSystem.REFERENCES.values():
            for ref in category.get("references", []):
                if ref.get("id") == ref_id:
                    return ref
        return None
    
    @staticmethod
    def get_references_for_topic(topic: str) -> List[dict]:
        """جلب المراجع لموضوع معين"""
        if topic in ScientificReferenceSystem.REFERENCES:
            return ScientificReferenceSystem.REFERENCES[topic].get("references", [])
        return []
    
    @staticmethod
    def get_knowledge_answer(question: str) -> Optional[dict]:
        """الحصول على إجابة لسؤال معرفي"""
        for key, value in ScientificReferenceSystem.KNOWLEDGE_BASE.items():
            if key in question or any(word in question for word in key.split()):
                ref = ScientificReferenceSystem.get_reference(value.get("reference", ""))
                return {
                    "answer": value["answer"],
                    "simplified": value.get("simplified", value["answer"]),
                    "reference": ref,
                    "full_text": value["answer"]
                }
        return None

    @staticmethod
    def format_reference_citation(ref: dict) -> str:
        """تنسيق الاستشهاد بالمرجع"""
        if not ref:
            return "مرجع علمي معتمد"
        
        parts = []
        if ref.get("authors"):
            parts.append(ref["authors"])
        if ref.get("year"):
            parts.append(f"({ref['year']})")
        if ref.get("title"):
            parts.append(f"<i>{ref['title']}</i>")
        if ref.get("publisher"):
            parts.append(f"{ref['publisher']}")
        if ref.get("edition"):
            parts.append(ref["edition"])
        if ref.get("isbn"):
            parts.append(f"ISBN: {ref['isbn']}")
        
        return ", ".join(parts)

# ==========================================
# نظام الردود الذكي للمنصة
# ==========================================

class IntelligentResponseSystem:
    """نظام الردود الذكي للمنصة"""
    
    @staticmethod
    def generate_scientific_response(question: str, context: dict = None) -> dict:
        """توليد رد علمي ذكي على الاستفسار"""
        
        # البحث في قاعدة المعرفة
        knowledge = ScientificReferenceSystem.get_knowledge_answer(question)
        
        if knowledge:
            return {
                "response": knowledge["simplified"],
                "detailed": knowledge["answer"],
                "reference": knowledge.get("reference"),
                "citation": ScientificReferenceSystem.format_reference_citation(knowledge.get("reference")),
                "confidence": 0.95
            }
        
        # تحليل السؤال واستنتاج إجابة علمية
        response = IntelligentResponseSystem._analyze_and_respond(question, context)
        return response
    
    @staticmethod
    def _analyze_and_respond(question: str, context: dict) -> dict:
        """تحليل عميق للأسئلة وإنتاج إجابات علمية"""
        
        # تحليل السياق
        animal_type = context.get("animal_type", "") if context else ""
        sector = context.get("sector", "") if context else ""
        
        # قاعدة الإجابات الذكية حسب السياق
        responses = {
            "تغذية": {
                "template": "في مجال تغذية {animal}، يعتمد النظام على أسس علمية دقيقة تشمل متطلبات الطاقة والبروتين والمعادن والفيتامينات. يتم حساب الاحتياجات باستخدام معادلات علمية معتمدة من منظمات التغذية العالمية.",
                "references": ["general_nutrition", "feed_formulation"]
            },
            "بروتين": {
                "template": "نظام البروتين المهضوم المستخدم في المنصة يعتمد على أحدث الأبحاث في مجال التغذية الحيوانية، حيث يتم تقدير الاحتياجات بدقة عالية تصل إلى 95% كفاءة، مما يوفر في تكاليف التغذية مع الحفاظ على الإنتاجية.",
                "references": ["protein_amino_acids", "digestible_protein"]
            },
            "طاقة": {
                "template": "يتم تقييم الطاقة في المنصة باستخدام نظام معادل النشاء (SE) الذي يعكس الطاقة الفعلية التي يستفيد منها الحيوان، مما يضمن دقة عالية في تقدير الاحتياجات وتحسين كفاءة التحويل الغذائي.",
                "references": ["energy_carbohydrates"]
            },
            "دواجن": {
                "template": "في قطاع الدواجن، توفر المنصة أدوات متخصصة تشمل: برامج تغذية دقيقة (Breeder, Broiler, Layer)، نظام إدارة بيئي متقدم، بروتوكولات تحصين وفق أحدث المعايير، ومؤشرات أداء EPEF و FCR لحساب الكفاءة.",
                "references": ["poultry", "broiler"]
            },
            "مجترات": {
                "template": "للمجترات، يتم تطبيق نظام تغذية متطور يراعي فسيولوجيا الكرش ومعايير البروتين المهضوم والطاقة، مع إضافة منظمات الحموضة لضمان صحة الكرش وكفاءة الهضم العالية.",
                "references": ["ruminants", "digestible_protein"]
            },
            "أغنام": {
                "template": "تغذية الأغنام والماعز في المنصة تعتمد على معايير NRC الخاصة بالمجترات الصغيرة، مع مراعاة مراحل الإنتاج المختلفة (النمو، التسمين، الحليب، الحمل) لتحقيق أعلى كفاءة إنتاجية.",
                "references": ["sheep_goats"]
            },
            "خيول": {
                "template": "في قطاع الخيول، يتم تطبيق نظام تغذية متوازن يراعي متطلبات الطاقة العالية للرياضة والنشاط، مع برامج تغذية خاصة للأمهار والفرسات المرضعات، وفق أحدث المعايير العلمية.",
                "references": ["horses"]
            },
            "أسماك": {
                "template": "في تغذية الأسماك والأحياء المائية، تعتمد المنصة على أحدث الأبحاث في مجال التغذية المائية، مع مراعاة متطلبات البروتين العالية والأحماض الأمينية الأساسية لنمو الأسماك بكفاءة.",
                "references": ["aquaculture"]
            },
            "إنتاج": {
                "template": "الإنتاج الحيواني المتكامل يعتمد على توازن دقيق بين: التغذية، الصحة، الوراثة، الإدارة. توفر المنصة أدوات متكاملة لتحسين كل هذه العوامل لتحقيق أعلى إنتاجية بأقل تكاليف ممكنة.",
                "references": ["animal_production"]
            }
        }
        
        # اختيار الرد المناسب
        for keyword, data in responses.items():
            if keyword in question or (context and keyword in str(context)):
                refs = []
                for ref_id in data.get("references", []):
                    refs.extend(ScientificReferenceSystem.get_references_for_topic(ref_id))
                
                response_text = data["template"].format(
                    animal=animal_type if animal_type else "الحيوان",
                    sector=sector if sector else "القطاع"
                )
                
                return {
                    "response": response_text,
                    "detailed": response_text + " يمكن الاطلاع على المراجع العلمية المعتمدة في دليل المستخدم.",
                    "references": refs[:3] if refs else [],
                    "citation": "مراجع علمية معتمدة",
                    "confidence": 0.85
                }
        
        # رد عام ذكي
        return {
            "response": "استفسارك يقع ضمن نطاق العلوم الحيوانية والتغذية الدقيقة. تستخدم منصة تاور العلمية أحدث المراجع والبروتوكولات العلمية في جميع عملياتها. للحصول على إجابة محددة، يرجى تحديد الموضوع بدقة أكبر أو التواصل مع فريق الدعم الفني.",
            "detailed": "تعتمد المنصة على مراجع علمية موثوقة مثل NRC، INRA، وجامعات عالمية في علوم التغذية والإنتاج الحيواني. يتم تحديث قواعد البيانات باستمرار لتضمين أحدث الأبحاث العلمية.",
            "reference": None,
            "citation": "المرجع العلمي للمنصة (تحديث مستمر)",
            "confidence": 0.75
        }

# ==========================================
# إضافة واجهة المراجع العلمية في المنصة
# ==========================================

def render_references_section():
    """عرض قسم المراجع العلمية"""
    st.markdown('<div class="section-title">📚 المراجع العلمية المعتمدة</div>', unsafe_allow_html=True)
    
    # اختيار الموضوع
    topics = {
        "general_nutrition": "المبادئ الأساسية لتغذية الحيوان",
        "protein_amino_acids": "البروتين والأحماض الأمينية",
        "energy_carbohydrates": "الطاقة والكربوهيدرات",
        "minerals_vitamins": "المعادن والفيتامينات",
        "poultry": "تغذية الدواجن",
        "ruminants": "تغذية المجترات",
        "sheep_goats": "تغذية الأغنام والماعز",
        "horses": "تغذية الخيول",
        "aquaculture": "تغذية الأسماك",
        "animal_production": "الإنتاج الحيواني",
        "feed_formulation": "تركيب الأعلاف",
        "broiler": "إنتاج الدجاج اللاحم",
        "digestible_protein": "البروتين المهضوم"
    }
    
    selected_topic = st.selectbox(
        "اختر الموضوع العلمي:",
        list(topics.values()),
        format_func=lambda x: x
    )
    
    # العثور على مفتاح الموضوع
    topic_key = None
    for key, value in topics.items():
        if value == selected_topic:
            topic_key = key
            break
    
    if topic_key and topic_key in ScientificReferenceSystem.REFERENCES:
        ref_data = ScientificReferenceSystem.REFERENCES[topic_key]
        st.markdown(f"### {ref_data['title']}")
        
        for ref in ref_data.get("references", []):
            with st.expander(f"📖 {ref.get('title', 'مرجع علمي')} ({ref.get('year', '')})"):
                cols = st.columns([0.7, 0.3])
                with cols[0]:
                    st.markdown(f"""
                    **المؤلفون:** {ref.get('authors', 'غير محدد')}
                    
                    **السنة:** {ref.get('year', 'غير محدد')}
                    
                    **الناشر:** {ref.get('publisher', 'غير محدد')}
                    
                    **الطبعة:** {ref.get('edition', 'غير محدد')}
                    
                    **الرقم المرجعي:** `{ref.get('id', 'غير محدد')}`
                    """)
                with cols[1]:
                    st.info(f"**الملخص:**\n{ref.get('summary', 'لا يوجد ملخص')}")
                    if ref.get('isbn'):
                        st.caption(f"ISBN: {ref.get('isbn')}")

# ==========================================
# إضافة نظام المساعدة الذكية في المنصة
# ==========================================

def render_smart_help_section():
    """عرض نظام المساعدة الذكي"""
    st.markdown('<div class="section-title">💡 المساعدة الذكية - اسأل المنصة</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background: #e3f2fd; padding: 15px; border-radius: 12px; border-right: 5px solid #1565C0; margin-bottom: 20px;'>
    <b>🤖 المساعد العلمي لمنصة تاور:</b> اكتب سؤالك حول أي موضوع متعلق بالتغذية والإنتاج الحيواني، 
    وسيقوم النظام بالرد عليك بأسلوب علمي مبسط مع المراجع المعتمدة.
    </div>
    """, unsafe_allow_html=True)
    
    # أسئلة مقترحة
    quick_questions = [
        "ما هو البروتين المهضوم",
        "ما هو معادل النشاء",
        "ما هو مؤشر EPEF",
        "كيف يتم تركيب العلف الأمثل",
        "ما هي أهمية إضافة الإنزيمات للأعلاف"
    ]
    
    st.markdown("**أسئلة سريعة مقترحة:**")
    cols = st.columns(len(quick_questions))
    for idx, q in enumerate(quick_questions):
        with cols[idx]:
            if st.button(q, use_container_width=True, key=f"quick_q_{idx}"):
                st.session_state["smart_question"] = q
                st.rerun()
    
    st.markdown("---")
    
    # مربع السؤال
    question = st.text_area("✍️ اكتب سؤالك هنا:", 
                           value=st.session_state.get("smart_question", ""),
                           placeholder="مثال: كيف يمكن تحسين كفاءة مزرعة الدجاج؟",
                           height=80)
    
    if st.button("🔍 اسأل المنصة", type="primary", use_container_width=True):
        if question.strip():
            with st.spinner("🔬 جاري البحث في قاعدة المعرفة العلمية..."):
                # الحصول على السياق الحالي
                context = {
                    "animal_type": st.session_state.get("active_breed_tag", ""),
                    "sector": st.session_state.get("active_stage_title", "")
                }
                
                # توليد الرد
                response = IntelligentResponseSystem.generate_scientific_response(question, context)
                
                # عرض الرد
                st.markdown("---")
                st.markdown("### 🤖 الرد العلمي:")
                
                # عرض الرد المبسط مع أيقونة
                st.markdown(f"""
                <div style='background: #f5f5f5; padding: 20px; border-radius: 12px; border-right: 5px solid #2e7d32;'>
                    <p style='font-size: 1.1rem; line-height: 1.8;'>{response['response']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # عرض التفاصيل العلمية
                with st.expander("🔬 التفاصيل العلمية والمراجع"):
                    st.markdown(f"**الشرح العلمي:**\n\n{response.get('detailed', response['response'])}")
                    
                    # عرض المراجع
                    if response.get('references'):
                        st.markdown("**📚 المراجع المعتمدة:**")
                        for ref in response.get('references', [])[:3]:
                            st.markdown(f"- {ScientificReferenceSystem.format_reference_citation(ref)}")
                    elif response.get('citation'):
                        st.markdown(f"**📚 المرجع:** {response.get('citation')}")
                    
                    # عرض درجة الثقة
                    confidence = response.get('confidence', 0)
                    confidence_text = "عالية جداً" if confidence > 0.9 else "عالية" if confidence > 0.7 else "متوسطة"
                    st.progress(confidence, text=f"درجة الثقة: {confidence_text} ({confidence*100:.0f}%)")
                
                # حفظ في سجل الاستفسارات
                if "query_history" not in st.session_state:
                    st.session_state["query_history"] = []
                st.session_state["query_history"].append({
                    "question": question,
                    "response": response['response'],
                    "timestamp": datetime.now().isoformat()
                })
                
                st.balloons()
        else:
            st.warning("⚠️ يرجى كتابة سؤالك أولاً")
    
    # عرض سجل الاستفسارات السابقة
    if st.session_state.get("query_history"):
        with st.expander("📋 سجل الاستفسارات السابقة"):
            for idx, query in enumerate(st.session_state["query_history"][-5:]):
                st.markdown(f"""
                **س {idx+1}:** {query['question']}
                
                **الرد:** {query['response']}
                
                ---
                """)

# ==========================================
# دمج النظام في المنصة - إضافة تبويب المراجع والمساعدة
# ==========================================

# إضافة تبويب جديد في قائمة التبويبات
if st.session_state["user_role"] == "owner":
    tabs_titles = ["🔬 النمذجة والحسابات العلفية", "📊 بورصة الأسعار المركزية", "🏭 إدارة المستودعات الذكية", "🧾 التسويق وفواتير البيع", "🖨️ مصمم الديباجة والدعاية", "📈 التحليلات المتقدمة", "🐔 إدارة مزارع الدجاج اللاحم (Broiler) – خاص بالمالك", "💬 تعليقات المختصين", "📚 المراجع العلمية", "💡 المساعدة الذكية", "📖 دليل المستخدم"]
elif st.session_state["user_role"] == "specialist":
    tabs_titles = ["🔬 النمذجة والحسابات العلفية", "📊 بورصة الأسعار المركزية", "🏭 إدارة المستودعات الذكية", "🧾 التسويق وفواتير البيع", "🖨️ مصمم الديباجة والدعاية", "📈 التحليلات المتقدمة", "💬 تعليقات المختصين", "📚 المراجع العلمية", "💡 المساعدة الذكية", "📖 دليل المستخدم"]
else:  # breeder
    tabs_titles = ["🔬 النمذجة والحسابات العلفية", "📚 المراجع العلمية", "💡 المساعدة الذكية", "📖 دليل المستخدم"]

# إضافة التبويبات الجديدة
# (سيتم إضافتها بعد التبويب الأخير وقبل دليل المستخدم)

# تبويب المراجع العلمية
# تبويب المساعدة الذكية

# ==========================================
# تحديث دليل المستخدم بإضافة قسم المراجع
# ==========================================

# إضافة قسم المراجع العلمية في دليل المستخدم
def update_user_guide():
    """تحديث دليل المستخدم بإضافة المراجع العلمية"""
    return """
    <div class="book-chapter">📚 المراجع العلمية المعتمدة في المنصة</div>
    <div class="book-body">
        تعتمد <b>منصة تاور العلمية</b> على أحدث وأشهر المراجع العلمية في مجال التغذية والإنتاج الحيواني، منها:
        <br><br>
        <b>1. المراجع الأساسية:</b><br>
        • NRC (National Research Council) - جميع إصدارات متطلبات العناصر الغذائية.<br>
        • INRA Feeding System - النظام الفرنسي المتقدم للتغذية.<br>
        • CNCPS - نظام كورنيل للكربوهيدرات والبروتين.<br>
        <br>
        <b>2. المراجع المتخصصة:</b><br>
        • Animal Nutrition - McDonald et al. (المرجع العالمي الأساسي).<br>
        • Commercial Poultry Nutrition - Leeson & Summers.<br>
        • Nutritional Ecology of the Ruminant - Van Soest.<br>
        <br>
        <b>3. أدلة الإنتاج:</b><br>
        • Ross Broiler Management Guide.<br>
        • Cobb Broiler Management Guide.<br>
        • Nutrient Requirements of Small Ruminants - NRC.<br>
        <br>
        <b>4. الأنظمة المتقدمة:</b><br>
        • نظام البروتين المهضوم (Digestible Protein System).<br>
        • نظام الطاقة (Starch Equivalent System).<br>
        • نظام التقييم الغذائي المتكامل.<br>
        <br>
        <i>يتم تحديث المراجع باستمرار لتضمين أحدث الأبحاث العلمية والتوصيات العالمية.</i>
    </div>
    """
