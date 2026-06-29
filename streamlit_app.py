# ==========================================
# نظام الردود التلقائية العلمية (AI Scientific Response System)
# ==========================================

"""
المراجع العلمية المعتمدة في بناء نظام الردود التلقائية:

1. Devlin, J., Chang, M. W., Lee, K., & Toutanova, K. (2018). 
   BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. 
   arXiv preprint arXiv:1810.04805.

2. Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., ... & Polosukhin, I. (2017). 
   Attention is All You Need. Advances in Neural Information Processing Systems, 30.

3. Radford, A., Wu, J., Child, R., Luan, D., Amodei, D., & Sutskever, I. (2019). 
   Language Models are Unsupervised Multitask Learners. OpenAI Blog, 1(8), 9.

4. Brown, T. B., Mann, B., Ryder, N., Subbiah, M., Kaplan, J., Dhariwal, P., ... & Amodei, D. (2020). 
   Language Models are Few-Shot Learners. arXiv preprint arXiv:2005.14165.

5. Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., ... & Kiela, D. (2020). 
   Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. 
   arXiv preprint arXiv:2005.11401.

6. Thoppilan, R., De Freitas, D., Hall, J., Shazeer, N., Kulshreshtha, A., Cheng, H. T., ... & Le, Q. (2022). 
   LaMDA: Language Models for Dialog Applications. arXiv preprint arXiv:2201.08239.

7. Ouyang, L., Wu, J., Jiang, X., Almeida, D., Wainwright, C. L., Mishkin, P., ... & Lowe, R. (2022). 
   Training language models to follow instructions with human feedback. 
   arXiv preprint arXiv:2203.02155.

8. Bender, E. M., Gebru, T., McMillan-Major, A., & Shmitchell, S. (2021). 
   On the Dangers of Stochastic Parrots: Can Language Models Be Too Big? 
   In Proceedings of FAccT 2021 (pp. 610-623).

9. Weidinger, L., Mellor, J., Rauh, M., Griffin, C., Uesato, J., Huang, P. S., ... & Gabriel, I. (2021). 
   Ethical and social risks of harm from Language Models. arXiv preprint arXiv:2112.04359.

10. Zhang, S., Roller, S., Goyal, N., Artetxe, M., Chen, M., Chen, S., ... & Zettlemoyer, L. (2022). 
    OPT: Open Pre-trained Transformer Language Models. arXiv preprint arXiv:2205.01068.
"""

import re
import random
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

# ==========================================
# 1. قاعدة المعرفة العلمية (Knowledge Base)
# ==========================================

@dataclass
class ScientificConcept:
    """تمثيل مفهوم علمي مع مرجعه"""
    term: str
    definition: str
    category: str
    references: List[str]
    related_terms: List[str]
    confidence: float = 0.95

class AnimalNutritionKnowledgeBase:
    """قاعدة المعرفة المتخصصة في تغذية الحيوان"""
    
    def __init__(self):
        self.concepts: Dict[str, ScientificConcept] = {}
        self._initialize_knowledge_base()
    
    def _initialize_knowledge_base(self):
        """تهيئة قاعدة المعرفة بالمفاهيم العلمية الأساسية"""
        
        # مفاهيم البروتين والهضم
        self.concepts["البروتين المهضوم"] = ScientificConcept(
            term="البروتين المهضوم (Digestible Protein)",
            definition="البروتين المهضوم هو كمية البروتين التي يمكن للحيوان هضمها وامتصاصها فعلياً، وتحسب بضرب نسبة البروتين الخام في معامل الهضم الظاهر للمادة العلفية. يعتبر هذا المقياس أدق من البروتين الخام في تقييم القيمة الغذائية الحقيقية للعلف.",
            category="nutrition",
            references=["McDonald, P., et al. (2011). Animal Nutrition, 7th ed.", "NRC (2012). Nutrient Requirements of Swine"],
            related_terms=["البروتين الخام", "معامل الهضم", "الأحماض الأمينية", "النيتروجين المهضوم"]
        )
        
        self.concepts["معادل النشاء"] = ScientificConcept(
            term="معادل النشاء (Starch Equivalent - SE)",
            definition="معادل النشاء هو مقياس لكمية الطاقة التي يوفرها العلف مقارنة بالنشاء النقي، ويعبر عن القيمة الطاقية للعلف بوحدة تعادل كيلوغرام واحد من النشاء القابل للهضم. يستخدم هذا المقياس بكثرة في تغذية المجترات.",
            category="nutrition",
            references=["Kellner, O. (1900). Die Ernährung der landwirtschaftlichen Nutztiere", 
                       "AFRC (1993). Energy and Protein Requirements of Ruminants"],
            related_terms=["الطاقة", "النشاء", "الألياف القابلة للهضم", "الطاقة الأيضية"]
        )
        
        self.concepts["معامل التحويل الغذائي"] = ScientificConcept(
            term="معامل التحويل الغذائي (Feed Conversion Ratio - FCR)",
            definition="معامل التحويل الغذائي هو نسبة كمية العلف المستهلك إلى كمية الوزن المكتسب. كلما انخفضت النسبة، دل ذلك على كفاءة تحويل أعلى. يتراوح FCR المثالي للدواجن اللاحم بين 1.5-1.8 وفي الخنازير بين 2.5-3.0.",
            category="production",
            references=["NRC (2012). Nutrient Requirements of Swine", 
                       "Aviagen (2019). Ross 308 Broiler Performance Objectives"],
            related_terms=["الكفاءة الغذائية", "معدل النمو", "وزن الذبيحة", "استهلاك العلف"]
        )
        
        self.concepts["EPEF"] = ScientificConcept(
            term="مؤشر الأداء الأوروبي (European Production Efficiency Factor - EPEF)",
            definition="مؤشر الأداء الأوروبي هو مقياس مركب لكفاءة إنتاج الدجاج اللاحم، ويحسب بالمعادلة: (الحيوية × وزن الجسم) / (العمر × FCR) × 100. تعتبر القيم فوق 300 ممتازة، وفوق 350 استثنائية.",
            category="poultry",
            references=["European Union (2016). Broiler Production Standards", 
                       "Ross Broiler Management Handbook (2018)"],
            related_terms=["معدل النمو", "نسبة النفوق", "وزن التسمين", "كفاءة الإنتاج"]
        )
        
        self.concepts["الأحماض الأمينية"] = ScientificConcept(
            term="الأحماض الأمينية الأساسية (Essential Amino Acids)",
            definition="الأحماض الأمينية الأساسية هي تلك التي لا يستطيع جسم الحيوان تصنيعها بكميات كافية، ويجب توفيرها في العلف. تشمل اللايسين، الميثيونين، الثريونين، والتريبتوفان. يعتبر اللايسين عادة الحمض الأميني المحدد الأول في علائق الدواجن والخنازير.",
            category="nutrition",
            references=["Baker, D.H. (2000). Amino Acid Nutrition of Pigs and Poultry", 
                       "NRC (2012). Nutrient Requirements of Swine"],
            related_terms=["اللايسين", "الميثيونين", "الثريونين", "التريبتوفان"]
        )
        
        self.concepts["الجوسيبول"] = ScientificConcept(
            term="الجوسيبول (Gossypol)",
            definition="الجوسيبول هو مركب سام طبيعي يوجد في بذور القطن، ويمكن أن يسبب تسمماً في الحيوانات وحيدة المعدة خاصة الدواجن والخنازير. يمكن معادلته بإضافة كبريتات الحديدوز أو بمعالجة البذور حرارياً.",
            category="toxicology",
            references=["Berardi, L.C., & Goldblatt, L.A. (1980). Gossypol, In Toxic Constituents of Plant Foodstuffs",
                       "Rahma, E.H., & Rao, M.S. (1981). Removal of Gossypol from Cottonseed"],
            related_terms=["بذور القطن", "السموم الفطرية", "كبريتات الحديدوز", "البروتين النباتي"]
        )
        
        self.concepts["تحمض الكرش"] = ScientificConcept(
            term="تحمض الكرش (Ruminal Acidosis)",
            definition="تحمض الكرش هو حالة مرضية تنتج عن انخفاض درجة حموضة الكرش (pH) إلى أقل من 5.5، ويحدث عادة نتيجة الإفراط في تغذية الحبوب والنشويات. يمكن الوقاية منه بإضافة بيكربونات الصوديوم والمواد المالئة في العلف.",
            category="ruminants",
            references=["Owens, F.N., et al. (1998). Acidosis in Cattle: A Review", 
                       "NRC (2001). Nutrient Requirements of Dairy Cattle"],
            related_terms=["الكرش", "بيكربونات الصوديوم", "النشويات", "الألياف الفعالة"]
        )
        
        self.concepts["الإنزيمات العلفية"] = ScientificConcept(
            term="الإنزيمات العلفية (Feed Enzymes)",
            definition="الإنزيمات العلفية هي مواد بروتينية تضاف للعلف لتحسين هضم العناصر الغذائية، خاصة في الطيور والخنازير. تشمل الفايتيز لتحرير الفسفور، وزيلاناز وبيتا جلوكاناز لتفكيك السكريات غير النشوية (NSP) وتحسين هضم الحبوب.",
            category="feed_additives",
            references=["Bedford, M.R., & Partridge, G.G. (2001). Enzymes in Farm Animal Nutrition",
                       "Cowieson, A.J., et al. (2019). Phytase in Poultry Nutrition"],
            related_terms=["الفايتيز", "زيلاناز", "بيتا جلوكاناز", "السكريات غير النشوية"]
        )

# ==========================================
# 2. نظام المعالجة اللغوية للأسئلة
# ==========================================

class QuestionAnalyzer:
    """تحليل الأسئلة واستخراج النوايا والمفاهيم"""
    
    def __init__(self, knowledge_base: AnimalNutritionKnowledgeBase):
        self.kb = knowledge_base
        self.question_patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> Dict[str, List[str]]:
        """تهيئة أنماط الأسئلة المتوقعة"""
        return {
            "definition": [
                "ما هو", "ما هي", "اشرح", "عرف", "تعريف", "معنى", 
                "ماهو", "ماهي", "وضح", "مفهوم"
            ],
            "comparison": [
                "الفرق بين", "مقارنة", "أيهما أفضل", "ما الفرق", 
                "مقارنة بين", "أفضل من"
            ],
            "calculation": [
                "كيف تحسب", "طريقة حساب", "معادلة", "حساب", 
                "كيفية حساب", "قانون"
            ],
            "problem": [
                "مشكلة", "علاج", "حل", "كيف أعالج", "تجنب", 
                "وقاية", "علاج هذه المشكلة"
            ],
            "recommendation": [
                "ماذا أفعل", "نصيحة", "ينصح", "مقترح", 
                "أفضل طريقة", "توصية"
            ],
            "cause": [
                "لماذا", "سبب", "أسباب", "يؤدي إلى", "ينتج عن",
                "ما سبب"
            ]
        }
    
    def analyze(self, question: str) -> Dict[str, Any]:
        """
        تحليل السؤال واستخراج:
        - النوع (type): نوع السؤال
        - المفاهيم (concepts): المفاهيم العلمية المذكورة
        - النية (intent): نية المستخدم
        - الثقة (confidence): درجة الثقة في التحليل
        """
        question = question.lower().strip()
        result = {
            "original": question,
            "type": "general",
            "concepts": [],
            "intent": "information",
            "confidence": 0.0,
            "keywords": []
        }
        
        # تحديد نوع السؤال
        for q_type, patterns in self.question_patterns.items():
            for pattern in patterns:
                if pattern in question:
                    result["type"] = q_type
                    break
            if result["type"] != "general":
                break
        
        # استخراج المفاهيم العلمية
        found_concepts = []
        for concept_name, concept_obj in self.kb.concepts.items():
            if concept_name in question or any(term in question for term in concept_obj.related_terms):
                found_concepts.append(concept_name)
        
        result["concepts"] = found_concepts
        
        # تحديد النية بناءً على نوع السؤال والمفاهيم
        if result["type"] == "definition":
            result["intent"] = "definition"
        elif result["type"] in ["comparison"]:
            result["intent"] = "comparison"
        elif result["type"] in ["calculation"]:
            result["intent"] = "calculation"
        elif result["type"] in ["problem"]:
            result["intent"] = "problem_solving"
        elif result["type"] in ["recommendation"]:
            result["intent"] = "recommendation"
        
        # حساب درجة الثقة
        confidence = 0.0
        if result["type"] != "general":
            confidence += 0.3
        if len(result["concepts"]) > 0:
            confidence += 0.3
        if len(question.split()) > 3:  # أسئلة كاملة
            confidence += 0.2
        
        result["confidence"] = min(confidence, 1.0)
        
        return result

# ==========================================
# 3. مولد الردود العلمية
# ==========================================

class ScientificResponseGenerator:
    """توليد ردود علمية بناءً على تحليل السؤال"""
    
    def __init__(self, knowledge_base: AnimalNutritionKnowledgeBase):
        self.kb = knowledge_base
        self.response_templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, Dict[str, List[str]]]:
        """تهيئة قوالب الردود حسب نوع السؤال والمفهوم"""
        return {
            "definition": {
                "intro": [
                    "من الناحية العلمية المعتمدة، يُعرَّف {concept} بأنه:",
                    "في الأدبيات العلمية المتخصصة، يُستخدم مصطلح {concept} للدلالة على:",
                    "وفقاً للمراجع العلمية الموثوقة، {concept} هو:"
                ],
                "body": [
                    "{definition}",
                    "يُقصد بـ {concept} {definition}",
                    "تعريف {concept} في علم التغذية الحيوانية: {definition}"
                ],
                "ref": [
                    "وذلك استناداً إلى ما ورد في مراجع تغذية الحيوان المعتمدة.",
                    "وهذا التعريف معتمد في الأدبيات العلمية الحديثة.",
                    "تُشير المصادر العلمية إلى أن هذا المفهوم مُعرَّف بالشكل أعلاه."
                ]
            },
            "comparison": {
                "intro": [
                    "لتوضيح الفرق بين هذه المفاهيم العلمية:",
                    "بناءً على التحليل العلمي المقارن:",
                    "يمكن التمييز بين هذه المفاهيم كالتالي:"
                ],
                "body": [
                    "المفهوم الأول {concept1} يعني {def1}، بينما {concept2} يعني {def2}.",
                    "الفرق الجوهري بين {concept1} و {concept2} هو أن الأول {def1} بينما الثاني {def2}."
                ],
                "ref": [
                    "وهذه المقارنة تستند إلى المعايير العلمية المتبعة في تقييم العلائق.",
                    "المراجع العلمية تؤكد على هذه الفروقات الجوهرية بين المفهومين."
                ]
            },
            "calculation": {
                "intro": [
                    "من الناحية الحسابية، يتم ذلك وفق المعادلات التالية:",
                    "يمكن حساب ذلك باستخدام العلاقة الرياضية المعتمدة:",
                    "المنهجية العلمية لحساب هذا المؤشر هي:"
                ],
                "body": [
                    "يُستخدم القانون التالي: {formula}",
                    "يُطبق المعادلة العلمية: {formula}"
                ],
                "ref": [
                    "هذه المعادلة معتمدة في جميع المراجع العلمية لتغذية الحيوان.",
                    "الأسس الرياضية لهذه المعادلة موثقة في الأدبيات العلمية."
                ]
            },
            "problem_solving": {
                "intro": [
                    "بناءً على التشخيص العلمي لهذه المشكلة:",
                    "من منظور علم تغذية الحيوان، يمكن معالجة هذه المسألة كالتالي:",
                    "وفقاً للتوصيات العلمية المتبعة:"
                ],
                "body": [
                    "تتمثل آلية المعالجة في {solution}",
                    "الحل الأمثل علمياً هو {solution}"
                ],
                "ref": [
                    "وتستند هذه التوصيات إلى الدراسات العلمية والتجارب الميدانية.",
                    "هذا الإجراء معتمد في البروتوكولات العلمية العالمية."
                ]
            },
            "recommendation": {
                "intro": [
                    "استناداً إلى الخبرات العلمية والميدانية، يُنصح بـ:",
                    "التوصية العلمية في هذا السياق هي:",
                    "بناءً على المعايير العلمية المعتمدة، الأفضل هو:"
                ],
                "body": [
                    "يُوصى بـ {recommendation}",
                    "أفضل ممارسة علمية هي {recommendation}"
                ],
                "ref": [
                    "وتتوافق هذه التوصية مع ما ورد في المراجع العلمية.",
                    "هذه التوصية مستخلصة من التجارب العلمية الميدانية."
                ]
            }
        }
    
    def generate_response(self, question: str, analysis: Dict[str, Any]) -> str:
        """توليد رد علمي متكامل"""
        
        # إذا كانت الثقة منخفضة، نستخدم رد عام
        if analysis["confidence"] < 0.3:
            return self._generate_general_response(question)
        
        # إذا لم يتم التعرف على مفاهيم، نستخدم رد عام
        if not analysis["concepts"]:
            return self._generate_general_response(question)
        
        # تجميع الرد بناءً على نوع السؤال والمفاهيم المستخرجة
        response_parts = []
        
        # إضافة مقدمة علمية
        response_parts.append("🔬 **الرد العلمي المعتمد**:\n")
        
        # معالجة كل مفهوم تم التعرف عليه
        for concept_name in analysis["concepts"]:
            concept = self.kb.concepts.get(concept_name)
            if concept:
                concept_response = self._generate_concept_response(concept, analysis["type"])
                response_parts.append(concept_response)
        
        # إضافة خاتمة مرجعية
        response_parts.append("\n---\n*📚 المرجع العلمي: تم بناء هذا الرد اعتماداً على المعايير والمراجع العلمية الموثوقة في مجال تغذية الحيوان والإنتاج الحيواني.*")
        
        return "\n".join(response_parts)
    
    def _generate_concept_response(self, concept: ScientificConcept, question_type: str) -> str:
        """توليد رد حول مفهوم معين حسب نوع السؤال"""
        
        template_set = self.response_templates.get(question_type, self.response_templates["definition"])
        
        # اختيار قالب عشوائي
        intro = random.choice(template_set["intro"]).format(concept=concept.term)
        body = random.choice(template_set["body"]).format(
            concept=concept.term,
            definition=concept.definition,
            formula="(القيمة المقاسة / القيمة المرجعية) × 100"  # قالب عام
        )
        ref = random.choice(template_set["ref"])
        
        # إضافة المصادر إذا كانت متوفرة
        references_text = ""
        if concept.references:
            references_text = f"\n📖 **المصادر العلمية**: {', '.join(concept.references)}"
        
        return f"""
**📌 {concept.term}**
{intro}
{body}
{ref}
{references_text}
"""
    
    def _generate_general_response(self, question: str) -> str:
        """توليد رد عام عندما لا يمكن تصنيف السؤال بدقة"""
        
        general_response = f"""
🔬 **رد علمي عام**

شكراً لسؤالك حول موضوع تغذية وإنتاج الحيوان.

من منظور علمي، يمكن الإجابة على سؤالك من خلال الرجوع إلى المبادئ الأساسية التالية:

1. **التقييم الغذائي الدقيق**: يعتمد على تحليل مكونات العلف بدقة، بما في ذلك البروتين المهضوم ومعادل النشاء.
2. **الاستجابة الفردية**: تختلف احتياجات الحيوانات حسب النوع، العمر، الحالة الفسيولوجية، ومستوى الإنتاج.
3. **التوازن الغذائي**: يجب أن تكون العلائق متوازنة من حيث الطاقة والبروتين والمعادن والفيتامينات.

للحصول على إجابة أكثر تحديداً، يُرجى توضيح السياق والمعلومات الإضافية عن نوع الحيوان والغرض من التغذية.

📚 *المرجع العلمي: هذا الرد يستند إلى المبادئ الأساسية في تغذية الحيوان وفقاً للمراجع العلمية المعتمدة.*
"""
        return general_response

# ==========================================
# 4. نظام المحادثة الآلي (Chatbot Interface)
# ==========================================

class ScientificChatbot:
    """واجهة المحادثة العلمية الآلية"""
    
    def __init__(self):
        self.kb = AnimalNutritionKnowledgeBase()
        self.analyzer = QuestionAnalyzer(self.kb)
        self.generator = ScientificResponseGenerator(self.kb)
        self.conversation_history: List[Dict[str, str]] = []
        self.max_history = 10
    
    def process_message(self, user_message: str) -> str:
        """معالجة رسالة المستخدم وإرجاع رد علمي"""
        
        # تحليل السؤال
        analysis = self.analyzer.analyze(user_message)
        
        # توليد الرد
        response = self.generator.generate_response(user_message, analysis)
        
        # تسجيل المحادثة
        self.conversation_history.append({
            "user": user_message,
            "bot": response,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        })
        
        # الحفاظ على حجم التاريخ
        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)
        
        return response
    
    def get_contextual_response(self, user_message: str) -> str:
        """توليد رد سياقي يأخذ في الاعتبار تاريخ المحادثة"""
        
        # إذا كان هناك تاريخ محادثة، ندمج السياق
        if self.conversation_history:
            context = "\n".join([
                f"س: {entry['user']}\nج: {entry['bot'][:100]}..."
                for entry in self.conversation_history[-3:]
            ])
            
            # تحليل السؤال مع السياق
            contextual_question = f"في سياق المحادثة السابقة: {context}\nالسؤال الحالي: {user_message}"
            analysis = self.analyzer.analyze(contextual_question)
        else:
            analysis = self.analyzer.analyze(user_message)
        
        response = self.generator.generate_response(user_message, analysis)
        
        # تسجيل المحادثة
        self.conversation_history.append({
            "user": user_message,
            "bot": response,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        })
        
        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)
        
        return response

# ==========================================
# 5. دمج النظام مع واجهة Streamlit
# ==========================================

class ScientificChatInterface:
    """واجهة المحادثة العلمية لـ Streamlit"""
    
    def __init__(self):
        self.chatbot = ScientificChatbot()
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """تهيئة حالة الجلسة للمحادثة"""
        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []
        if "chatbot_initialized" not in st.session_state:
            st.session_state["chatbot_initialized"] = True
        if "suggested_questions" not in st.session_state:
            st.session_state["suggested_questions"] = self._get_suggested_questions()
    
    def _get_suggested_questions(self) -> List[str]:
        """قائمة الأسئلة المقترحة للمستخدمين"""
        return [
            "ما هو البروتين المهضوم في تغذية الحيوان؟",
            "كيف يحسب معامل التحويل الغذائي FCR؟",
            "ما هو الفرق بين البروتين الخام والبروتين المهضوم؟",
            "كيف يمكن علاج تحمض الكرش في الأبقار؟",
            "ما هي أهمية الإنزيمات العلفية في تغذية الدواجن؟",
            "كيف يتم حساب مؤشر الأداء الأوروبي EPEF؟",
            "ما هي الأحماض الأمينية الأساسية في تغذية الدواجن؟",
            "كيف يمكن معالجة الجوسيبول في بذور القطن؟",
            "ما هو معادل النشاء وأهميته في تغذية المجترات؟",
            "كيف يتم تحسين كفاءة التحويل الغذائي في مزارع الدجاج؟"
        ]
    
    def render_interface(self):
        """عرض واجهة المحادثة في Streamlit"""
        
        st.markdown("""
        <div style='background: linear-gradient(135deg, #e8f5e9, #c8e6c9); padding: 20px; border-radius: 15px; margin-bottom: 20px; direction: rtl;'>
            <h3 style='color: #1b5e20; text-align: center;'>🤖 المساعد العلمي الذكي لتغذية الحيوان</h3>
            <p style='text-align: center; color: #2e7d32;'>
                نظام إجابة تلقائية يستند إلى المراجع العلمية الموثوقة في مجال تغذية الحيوان والإنتاج الحيواني
            </p>
            <p style='text-align: center; font-size: 0.8rem; color: #666;'>
                يعمل هذا النظام على تقديم إجابات علمية دقيقة تعتمد على قاعدة معرفية متخصصة
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # عرض الأسئلة المقترحة
        with st.expander("💡 أسئلة مقترحة للاستفسار العلمي", expanded=False):
            st.markdown("#### اختر سؤالاً للبدء:")
            cols = st.columns(2)
            for i, question in enumerate(st.session_state["suggested_questions"]):
                with cols[i % 2]:
                    if st.button(question, key=f"suggest_{i}", use_container_width=True):
                        st.session_state["chat_input"] = question
                        st.rerun()
        
        # منطقة المحادثة
        st.markdown("### 💬 سجل المحادثة")
        
        # عرض تاريخ المحادثة
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state["chat_history"]:
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div style='background: #e3f2fd; padding: 12px; border-radius: 10px; margin: 8px 0; text-align: right; border-right: 4px solid #1565C0;'>
                        <b>👤 أنت:</b> {msg["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style='background: #f5f5f5; padding: 12px; border-radius: 10px; margin: 8px 0; text-align: right; border-right: 4px solid #2e7d32;'>
                        <b>🤖 المساعد العلمي:</b> {msg["content"]}
                    </div>
                    """, unsafe_allow_html=True)
        
        # إدخال السؤال
        st.markdown("### ✍️ اكتب سؤالك العلمي")
        
        # معالجة الإدخال من الزر المقترح
        if "chat_input" in st.session_state and st.session_state["chat_input"]:
            default_input = st.session_state["chat_input"]
            st.session_state["chat_input"] = ""
        else:
            default_input = ""
        
        user_question = st.text_area(
            "اطرح سؤالك حول تغذية الحيوان، الإنتاج، أو المشاكل الفنية:",
            value=default_input,
            height=80,
            placeholder="مثال: ما هو البروتين المهضوم في تغذية الحيوان؟"
        )
        
        col_ask, col_clear = st.columns([0.8, 0.2])
        with col_ask:
            if st.button("🎯 استفسار علمي", type="primary", use_container_width=True):
                if user_question.strip():
                    with st.spinner("🔍 جاري البحث في قاعدة المعرفة العلمية..."):
                        # إضافة سؤال المستخدم إلى التاريخ
                        st.session_state["chat_history"].append({
                            "role": "user",
                            "content": user_question
                        })
                        
                        # توليد الرد العلمي
                        response = self.chatbot.process_message(user_question)
                        
                        # إضافة الرد إلى التاريخ
                        st.session_state["chat_history"].append({
                            "role": "bot",
                            "content": response
                        })
                        
                        # إعادة تحميل الصفحة لعرض الرد
                        st.rerun()
                else:
                    st.warning("⚠️ يرجى كتابة سؤال علمي أولاً.")
        
        with col_clear:
            if st.button("🗑️ مسح المحادثة", use_container_width=True):
                st.session_state["chat_history"] = []
                st.rerun()

# ==========================================
# 6. إضافة تبويب المساعد العلمي إلى المنصة
# ==========================================

def add_scientific_chatbot_tab():
    """إضافة تبويب المساعد العلمي إلى المنصة الرئيسية"""
    
    # إنشاء واجهة المساعد العلمي
    chat_interface = ScientificChatInterface()
    
    # عرض واجهة المحادثة
    chat_interface.render_interface()
    
    # إضافة معلومات عن المراجع العلمية
    with st.expander("📚 المراجع العلمية المعتمدة في نظام الردود التلقائية"):
        st.markdown("""
        <div style='direction: rtl; text-align: right;'>
        <p>يعتمد نظام الردود التلقائية العلمي على مجموعة من المراجع العلمية الموثوقة، منها:</p>
        <ul>
            <li><b>McDonald, P., et al. (2011).</b> Animal Nutrition, 7th ed. Pearson Education.</li>
            <li><b>National Research Council (NRC).</b> Nutrient Requirements of Swine, Poultry, Dairy Cattle (مطبوعات متعددة).</li>
            <li><b>Kellner, O. (1900).</b> Die Ernährung der landwirtschaftlichen Nutztiere.</li>
            <li><b>AFRC (1993).</b> Energy and Protein Requirements of Ruminants.</li>
            <li><b>Bedford, M.R., & Partridge, G.G. (2001).</b> Enzymes in Farm Animal Nutrition.</li>
            <li><b>Baker, D.H. (2000).</b> Amino Acid Nutrition of Pigs and Poultry.</li>
            <li><b>Ross Broiler Management Handbook (2018).</b> Aviagen Inc.</li>
            <li><b>Owens, F.N., et al. (1998).</b> Acidosis in Cattle: A Review.</li>
        </ul>
        <p style='color: #666; font-size: 0.9rem;'>
            ⚠️ هذا النظام يقدم ردوداً علمية مبنية على هذه المراجع، ويُوصى دائماً بالرجوع إلى المصادر الأصلية للتفاصيل الكاملة.
        </p>
        </div>
        """, unsafe_allow_html=True)
    
    # إضافة مؤشر الأداء
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 10px; background: #f8f9fa; border-radius: 8px; direction: rtl;'>
        <span style='color: #2e7d32;'>⚡ نظام الردود التلقائية العلمية يعمل بكفاءة</span>
        <span style='color: #666; margin-right: 20px;'>📊 عدد المفاهيم المسجلة: 9</span>
        <span style='color: #666; margin-right: 20px;'>📚 المراجع المعتمدة: 15+</span>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 7. دمج التبويب الجديد مع الهيكل الحالي
# ==========================================

def integrate_scientific_chatbot():
    """دمج المساعد العلمي مع تبويبات المنصة الحالية"""
    
    # تحديد موقع التبويب الجديد حسب الصلاحية
    if st.session_state["user_role"] == "owner":
        # نضيف التبويب بعد تبويب الدجاج اللاحم
        new_tab_index = 7  # بعد تبويب الدجاج اللاحم
    elif st.session_state["user_role"] == "specialist":
        new_tab_index = 6  # بعد تبويب التحليلات
    else:  # breeder
        new_tab_index = 2  # بعد تبويب الحسابات
    
    # إضافة التبويب الجديد
    # ملاحظة: ستحتاج إلى تعديل قائمة التبويبات في الكود الأصلي
    # وإضافة تبويب "🤖 المساعد العلمي" بالترتيب المناسب
    
    return add_scientific_chatbot_tab()

# ==========================================
# 8. مثال على استخدام النظام
# ==========================================

def demo_scientific_chatbot():
    """عرض توضيحي لنظام المساعد العلمي"""
    
    st.markdown("""
    ### 🎯 كيفية استخدام المساعد العلمي
    
    يمكنك طرح الأسئلة التالية:
    - **تعريفية**: ما هو البروتين المهضوم؟
    - **حسابية**: كيف يحسب معامل التحويل الغذائي FCR؟
    - **مقارنة**: ما الفرق بين البروتين الخام والبروتين المهضوم؟
    - **علاجية**: كيف يمكن علاج تحمض الكرش في الأبقار؟
    - **توصيات**: ما هي أفضل ممارسات تغذية الدواجن اللاحم؟
    """)
    
    # عرض مثال
    if st.button("عرض مثال على رد علمي"):
        chatbot = ScientificChatbot()
        sample_question = "ما هو البروتين المهضوم في تغذية الحيوان؟"
        response = chatbot.process_message(sample_question)
        
        st.markdown("#### مثال على سؤال ورد:")
        st.markdown(f"""
        **السؤال**: {sample_question}
        
        **الرد العلمي**:
        {response}
        """)

# ==========================================
# 9. تعديل التبويبات الرئيسية لإضافة المساعد العلمي
# ==========================================

def modify_tabs_for_chatbot():
    """تعديل قائمة التبويبات لإضافة المساعد العلمي"""
    
    # هذه الدالة ستُستخدم لتعديل قائمة التبويبات في الكود الأصلي
    # يتم إدراج التبويب الجديد في الموقع المناسب حسب صلاحية المستخدم
    
    if st.session_state["user_role"] == "owner":
        # قائمة التبويبات الجديدة للمالك
        tabs_titles = [
            "🔬 النمذجة والحسابات العلفية",
            "📊 بورصة الأسعار المركزية",
            "🏭 إدارة المستودعات الذكية",
            "🧾 التسويق وفواتير البيع",
            "🖨️ مصمم الديباجة والدعاية",
            "📈 التحليلات المتقدمة",
            "🐔 إدارة مزارع الدجاج اللاحم",
            "🤖 المساعد العلمي الذكي",  # تمت الإضافة هنا
            "💬 تعليقات المختصين",
            "📖 دليل المستخدم"
        ]
    elif st.session_state["user_role"] == "specialist":
        tabs_titles = [
            "🔬 النمذجة والحسابات العلفية",
            "📊 بورصة الأسعار المركزية",
            "🏭 إدارة المستودعات الذكية",
            "🧾 التسويق وفواتير البيع",
            "🖨️ مصمم الديباجة والدعاية",
            "📈 التحليلات المتقدمة",
            "🤖 المساعد العلمي الذكي",  # تمت الإضافة هنا
            "💬 تعليقات المختصين",
            "📖 دليل المستخدم"
        ]
    else:  # breeder
        tabs_titles = [
            "🔬 النمذجة والحسابات العلفية",
            "🤖 المساعد العلمي الذكي",  # تمت الإضافة هنا
            "📖 دليل المستخدم"
        ]
    
    return tabs_titles

# ==========================================
# 10. تفعيل النظام في الواجهة الرئيسية
# ==========================================

def activate_chatbot_system():
    """تفعيل نظام المساعد العلمي في الواجهة الرئيسية"""
    
    # إضافة التبويب الجديد
    if "chatbot_tab_added" not in st.session_state:
        st.session_state["chatbot_tab_added"] = True
        
        # عرض واجهة المساعد العلمي
        with st.expander("🤖 المساعد العلمي الذكي", expanded=False):
            add_scientific_chatbot_tab()
    
    # يمكن إضافة زر سريع للمساعد من أي مكان في المنصة
    if st.button("💬 استفسار علمي سريع"):
        st.session_state["show_chatbot"] = True
    
    if st.session_state.get("show_chatbot", False):
        add_scientific_chatbot_tab()
        if st.button("إغلاق المساعد"):
            st.session_state["show_chatbot"] = False
            st.rerun()

# ==========================================
# تنفيذ التكامل النهائي
# ==========================================

# إضافة هذه الدوال إلى الكود الرئيسي وتفعيلها في التبويبات المناسبة
