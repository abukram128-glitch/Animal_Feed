    def __init__(self):
        self.formula_history = []
        self.performance_data = {}
        self.knowledge_graph = {}
        self._initialize_knowledge_base()
    
    def _initialize_knowledge_base(self):
        """تهيئة قاعدة المعرفة"""
        self.knowledge_graph = {
            'seasonal_adjustments': {
                'summer': {
                    'energy_reduction': 0.95,
                    'protein_increase': 0.03,
                    'electrolyte_boost': True,
                    'vitamin_c': 200
                },
                'winter': {
                    'energy_increase': 0.05,
                    'protein_adjustment': 0.0,
                    'vitamin_d3': 500
                }
            },
            'stress_factors': {
                'heat_stress': {
                    'betaine': 1.0,
                    'sodium_bicarbonate': 2.0,
                    'potassium_chloride': 2.0
                },
                'vaccination': {
                    'vitamin_e': 100,
                    'selenium': 0.3,
                    'probiotics': True
                }
            }
        }
    
    def get_optimal_formula_recommendation(self, animal_type, target_weight, current_prices):
        """الحصول على توصيات التركيبة المثلى"""
        recommendations = {
            'cost_optimization': [],
            'seasonal_recommendations': []
        }
        
        current_month = datetime.now().month
        if current_month in [6, 7, 8]:
            recommendations['seasonal_recommendations'].append({
                'type': 'إجهاد حراري',
                'actions': [
                    'زيادة بيكربونات الصوديوم بنسبة 0.2%',
                    'إضافة بيتايين بمعدل 1 جم/كجم',
                    'رفع فيتامين C إلى 200 مجم/كجم'
                ]
            })
        
        expensive_ingredients = {
            name: price for name, price in current_prices.items() 
            if price > np.mean(list(current_prices.values()))
        }
        
        for ing, price in expensive_ingredients.items():
            alternatives = self._find_alternatives(ing, current_prices)
            if alternatives:
                recommendations['cost_optimization'].append({
                    'ingredient': ing,
                    'current_price': price,
                    'alternatives': alternatives[:3]
                })
        
        return recommendations
    
    def _find_alternatives(self, ingredient, prices):
        """البحث عن بدائل للمواد الخام"""
        alternatives = []
        nutritional_equivalents = {
            'ذرة صفراء': ['ذرة بيضاء', 'سورجم', 'قمح'],
            'كسب فول صويا 44%': ['كسب فول صويا 48%', 'أمباز الفول السوداني', 'كسب عباد الشمس 36%'],
            'نخالة قمح': ['سرسة الأرز', 'قشر فول سوداني']
        }
        
        if ingredient in nutritional_equivalents:
            for alt in nutritional_equivalents[ingredient]:
                if alt in prices:
                    savings = prices[ingredient] - prices[alt]
                    if savings > 0:
                        alternatives.append({
                            'name': alt,
                            'price': prices[alt],
                            'savings': savings,
                            'savings_percent': (savings / prices[ingredient]) * 100
                    })
        
        return sorted(alternatives, key=lambda x: x['savings'], reverse=True)


class AdvancedAnalytics:
    """نظام التحليلات المتقدمة مع تصورات ثلاثية الأبعاد"""
    
    def create_3d_visualization(self, data, x_col, y_col, z_col, color_col=None):
        """إنشاء تصور ثلاثي الأبعاد"""
        fig = go.Figure(data=[go.Scatter3d(
            x=data[x_col],
            y=data[y_col],
            z=data[z_col],
            mode='markers',
            marker=dict(
                size=8,
                color=data[color_col] if color_col else data[z_col],
                colorscale='Viridis',
                opacity=0.8,
                colorbar=dict(title=color_col if color_col else z_col)
            ),
            hovertemplate='<b>X:</b> %{x}<br><b>Y:</b> %{y}<br><b>Z:</b> %{z}<extra></extra>'
        )])
        
        fig.update_layout(
            scene=dict(
                xaxis_title=x_col,
                yaxis_title=y_col,
                zaxis_title=z_col,
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
            ),
            title='تحليل ثلاثي الأبعاد للأداء',
            template='plotly_dark',
            width=800,
            height=600
        )
        
        return fig
    
    def generate_heatmap_analysis(self, correlation_matrix):
        """توليد خريطة حرارية للارتباطات"""
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.index,
            colorscale='RdBu',
            zmid=0,
            text=np.round(correlation_matrix.values, 2),
            texttemplate='%{text}',
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title='مصفوفة الارتباط للمتغيرات',
            width=800,
            height=800,
            template='plotly_white'
        )
        
        return fig
    
    def perform_pca_analysis(self, data, n_components=3):
        """تحليل المكونات الرئيسية"""
        if not SKLEARN_AVAILABLE:
            return None
            
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(data)
        
        pca = PCA(n_components=n_components)
        pca_result = pca.fit_transform(scaled_data)
        
        explained_variance = pca.explained_variance_ratio_
        
        pca_df = pd.DataFrame(
            data=pca_result,
            columns=[f'PC{i+1}' for i in range(n_components)]
        )
        
        return {
            'transformed_data': pca_df,
            'explained_variance': explained_variance,
            'components': pca.components_,
            'loadings': pd.DataFrame(
                pca.components_.T,
                columns=[f'PC{i+1}' for i in range(n_components)],
                index=data.columns
            )
        }


class BigDataManager:
    """مدير البيانات الضخمة والتحليلات المتقدمة"""
    
    def __init__(self):
        self.data_lake = {}
    
    def ingest_real_time_data(self, source, data):
        """استيعاب البيانات في الوقت الحقيقي"""
        timestamp = datetime.now()
        if source not in self.data_lake:
            self.data_lake[source] = []
        
        self.data_lake[source].append({
            'timestamp': timestamp,
            'data': data,
            'metadata': {
                'source': source,
                'size_bytes': len(json.dumps(data))
            }
        })
        
        self._clean_old_data(source, max_age_hours=24)
        return timestamp
    
    def _clean_old_data(self, source, max_age_hours=24):
        """تنظيف البيانات القديمة"""
        if source in self.data_lake:
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            self.data_lake[source] = [
                entry for entry in self.data_lake[source]
                if entry['timestamp'] > cutoff_time
            ]
    
    def aggregate_data(self, source, time_window_minutes=60):
        """تجميع البيانات حسب النوافذ الزمنية"""
        if source not in self.data_lake:
            return {}
        
        aggregated = {}
        cutoff = datetime.now() - timedelta(minutes=time_window_minutes)
        
        for entry in self.data_lake[source]:
            if entry['timestamp'] > cutoff:
                time_key = entry['timestamp'].strftime('%H:%M')
                if time_key not in aggregated:
                    aggregated[time_key] = []
                aggregated[time_key].append(entry['data'])
        
        stats = {}
        for time_key, data_list in aggregated.items():
            if isinstance(data_list[0], dict):
                numeric_values = {}
                for key in data_list[0].keys():
                    values = [d[key] for d in data_list if isinstance(d[key], (int, float))]
                    if values:
                        numeric_values[key] = {
                            'mean': np.mean(values),
                            'std': np.std(values),
                            'min': np.min(values),
                            'max': np.max(values),
                            'count': len(values)
                        }
                stats[time_key] = numeric_values
        
        return stats


# ==========================================
# تهيئة الأنظمة المتقدمة
# ==========================================

@st.cache_resource
def initialize_advanced_systems():
    systems = {
        'ai_model': AdvancedAIModel(),
        'blockchain': BlockchainManager(),
        'iot_simulator': IoTSimulator(),
        'recommendation_system': IntelligentRecommendationSystem(),
        'advanced_analytics': AdvancedAnalytics(),
        'big_data_manager': BigDataManager()
    }
    return systems

# ==========================================
# 1. نظام قاعدة البيانات المحلية (SQLite)
# ==========================================
import sqlite3
from dataclasses import dataclass, asdict

class DatabaseManager:
    """مدير قاعدة البيانات المحلية"""
    def __init__(self, db_path="tower_platform.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """تهيئة الجداول"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # جدول المستخدمين
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (user_id TEXT PRIMARY KEY,
                      username TEXT UNIQUE,
                      password_hash TEXT,
                      role TEXT,
                      full_name TEXT,
                      email TEXT,
                      phone TEXT,
                      created_date TEXT)''')
        
        # جدول الدورات الإنتاجية
        c.execute('''CREATE TABLE IF NOT EXISTS farm_cycles
                     (cycle_id TEXT PRIMARY KEY,
                      farm_name TEXT,
                      animal_type TEXT,
                      breed TEXT,
                      start_date TEXT,
                      end_date TEXT,
                      initial_birds INTEGER,
                      final_weight_kg REAL,
                      total_feed_kg REAL,
                      total_dead INTEGER,
                      total_culled INTEGER,
                      fcr REAL,
                      adg REAL,
                      epef REAL,
                      mortality_rate REAL,
                      notes TEXT,
                      created_by TEXT,
                      created_date TEXT)''')
        
        # جدول الخلطات العلفية
        c.execute('''CREATE TABLE IF NOT EXISTS feed_formulas
                     (formula_id TEXT PRIMARY KEY,
                      formula_name TEXT,
                      animal_type TEXT,
                      target_dp REAL,
                      target_se REAL,
                      ingredients TEXT,
                      total_cost REAL,
                      created_by TEXT,
                      created_date TEXT)''')
        
        # جدول الفواتير
        c.execute('''CREATE TABLE IF NOT EXISTS invoices
                     (invoice_id TEXT PRIMARY KEY,
                      customer_name TEXT,
                      formula_id TEXT,
                      quantity_ton REAL,
                      unit_price REAL,
                      total_price REAL,
                      status TEXT,
                      created_by TEXT,
                      created_date TEXT)''')
        
        # جدول الأسعار التاريخية
        c.execute('''CREATE TABLE IF NOT EXISTS price_history
                     (record_id TEXT PRIMARY KEY,
                      ingredient_name TEXT,
                      price REAL,
                      currency TEXT,
                      country TEXT,
                      city TEXT,
                      record_date TEXT,
                      recorded_by TEXT)''')
        
        # جداول جديدة للأنظمة المتقدمة
        c.execute('''CREATE TABLE IF NOT EXISTS ai_predictions
                     (prediction_id TEXT PRIMARY KEY,
                      model_name TEXT,
                      input_data TEXT,
                      prediction REAL,
                      confidence REAL,
                      timestamp TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS blockchain_transactions
                     (tx_id TEXT PRIMARY KEY,
                      block_index INTEGER,
                      sender TEXT,
                      receiver TEXT,
                      data TEXT,
                      signature TEXT,
                      timestamp TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS iot_readings
                     (reading_id TEXT PRIMARY KEY,
                      sensor_type TEXT,
                      value REAL,
                      unit TEXT,
                      status TEXT,
                      farm_id TEXT,
                      timestamp TEXT)''')
        
        conn.commit()
        conn.close()
    
    def execute_query(self, query: str, params: tuple = ()):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        result = c.execute(query, params)
        conn.commit()
        data = result.fetchall()
        conn.close()
        return data
    
    def insert_record(self, table: str, data: dict):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        c.execute(query, list(data.values()))
        conn.commit()
        conn.close()

# ==========================================
# 2. نظام المصادقة المتقدم
# ==========================================
class AuthManager:
    def __init__(self):
        self.db = DatabaseManager()
        self._create_default_admin()
    
    def _create_default_admin(self):
        users = self.db.execute_query("SELECT * FROM users WHERE username='admin'")
        if not users:
            self.create_user('admin', 'admin123', 'owner', 'مدير النظام', 'admin@tower.com', '+249123456789')
    
    def create_user(self, username: str, password: str, role: str, full_name: str, email: str, phone: str):
        user_id = secrets.token_hex(16)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        data = {
            'user_id': user_id,
            'username': username,
            'password_hash': password_hash,
            'role': role,
            'full_name': full_name,
            'email': email,
            'phone': phone,
            'created_date': datetime.now().isoformat()
        }
        self.db.insert_record('users', data)
        return user_id
    
    def authenticate(self, username: str, password: str) -> Optional[dict]:
        users = self.db.execute_query("SELECT * FROM users WHERE username=?", (username,))
        if users:
            user = users[0]
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if user[2] == password_hash:
                return {
                    'user_id': user[0],
                    'username': user[1],
                    'role': user[3],
                    'full_name': user[4],
                    'email': user[5],
                    'phone': user[6]
                }
        return None

# ==========================================
# 3. نظام التنبؤ بالأسعار
# ==========================================
class PricePredictor:
    def __init__(self):
        self.db = DatabaseManager()
    
    def get_ingredient_prices(self, ingredient_name: str, days: int = 30) -> List[dict]:
        results = self.db.execute_query(
            "SELECT * FROM price_history WHERE ingredient_name=? ORDER BY record_date DESC LIMIT ?",
            (ingredient_name, days)
        )
        return [{
            'record_id': r[0],
            'ingredient_name': r[1],
            'price': r[2],
            'currency': r[3],
            'country': r[4],
            'city': r[5],
            'record_date': r[6]
        } for r in results]
    
    def predict_price(self, ingredient_name: str, days_ahead: int = 7) -> dict:
        prices = self.get_ingredient_prices(ingredient_name, 30)
        if len(prices) < 5:
            return {'prediction': None, 'confidence': 0}
        
        price_list = [p['price'] for p in prices]
        weights = np.array(range(1, len(price_list) + 1))
        weighted_avg = np.average(price_list, weights=weights)
        trend = (price_list[0] - price_list[-1]) / len(price_list) if len(price_list) > 1 else 0
        prediction = weighted_avg + (trend * days_ahead)
        
        return {
            'prediction': max(0, prediction),
            'confidence': min(1, len(price_list) / 30),
            'current_price': price_list[0] if price_list else None,
            'trend': 'up' if trend > 0 else 'down' if trend < 0 else 'stable'
        }

# ==========================================
# 4. نظام المراجع العلمية
# ==========================================
class ScientificReferenceSystem:
    REFERENCES = {
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
                }
            ]
        }
    }
    
    KNOWLEDGE_BASE = {
        "ما هو البروتين المهضوم": {
            "answer": "البروتين المهضوم (Digestible Protein) هو كمية البروتين التي يستطيع الحيوان هضمها وامتصاصها فعلياً من العلف.",
            "reference": "REF023",
            "simplified": "البروتين المهضوم هو الجزء من البروتين الذي يستفيد منه الحيوان فعلياً."
        }
    }
    
    @staticmethod
    def get_reference(ref_id: str) -> Optional[dict]:
        for category in ScientificReferenceSystem.REFERENCES.values():
            for ref in category.get("references", []):
                if ref.get("id") == ref_id:
                    return ref
        return None

# ==========================================
# 5. إعدادات المنصة
# ==========================================
st.set_page_config(
    page_title="منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

@st.cache_resource
def init_caching_system():
    return {
        "cache_hits": 0,
        "cache_misses": 0,
        "last_cleanup": datetime.now()
    }

CACHE_SYSTEM = init_caching_system()

# تهيئة الأنظمة المتقدمة
ADVANCED_SYSTEMS = initialize_advanced_systems()

CODES_DB = {
    "202687": {"role": "owner", "name": "الاختصاصي م. عبد القادر إسماعيل تاور", "level": 3},
    "2020": {"role": "specialist", "name": "المختص والزملاء", "level": 2},
    "2026": {"role": "breeder", "name": "المربي", "level": 1}
}

PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG", "1000069464.JPG"]

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "abukram128@gmail.com"
SENDER_PASSWORD = "oynz rdli tsdy ekdq"
OWNER_EMAIL = "abukram128@gmail.com"
WHATSAPP_NUMBER = "+249123533489"

@st.cache_data(ttl=3600)
def get_image_base64(paths: List[str]) -> Optional[str]:
    for path in paths:
        if os.path.exists(path):
            try:
                with open(path, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode()
            except Exception:
                pass
    return None

img_base64 = get_image_base64(PHOTO_OPTIONS)

class ArabicTextProcessor:
    @staticmethod
    @lru_cache(maxsize=1000)
    def fix_arabic_text(text: str) -> str:
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        return bidi_text

arabic_processor = ArabicTextProcessor()

# ==========================================
# 6. مولد PDF
# ==========================================
class ProfessionalPDFGenerator:
    def __init__(self):
        self.font_name = 'Helvetica'
        if os.path.exists("Amiri-Regular.ttf"):
            try:
                pdfmetrics.registerFont(TTFont('Amiri', 'Amiri-Regular.ttf'))
                self.font_name = 'Amiri'
            except:
                pass

    def generate_comprehensive_report(self, formula, target_dp, breed, cost, city, local_cost, local_sym, computed_se, include_charts=True) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
        story = []

        def p(text, size=12, align=TA_RIGHT, color=HexColor('#000000')):
            safe_text = arabic_processor.fix_arabic_text(str(text))
            return Paragraph(safe_text, ParagraphStyle('style', fontName=self.font_name, fontSize=size, alignment=align, textColor=color, spaceAfter=6, leading=size*1.5))

        story.append(p("تقرير فني شامل - منصة تاور العلمية", size=22, align=TA_CENTER, color=HexColor('#1b5e20')))
        story.append(Spacer(1, 12))
        for line in [f"المشرف العام: الاختصاصي م. عبد القادر إسماعيل تاور", f"الموقع الجغرافي: {city}", f"الفصيل المستهدف: {breed}", f"تاريخ الإصدار: {datetime.now().strftime('%Y-%m-%d %H:%M')}"]:
            story.append(p(line, size=11))
        story.append(Spacer(1, 15))

        tdata = [
            [arabic_processor.fix_arabic_text('المعيار'), arabic_processor.fix_arabic_text('القيمة')],
            [arabic_processor.fix_arabic_text('البروتين المهضوم (DP)'), f'{target_dp:.2f}%'],
            [arabic_processor.fix_arabic_text('معادل النشاء (SE)'), f'{computed_se:.2f} وحدة'],
            [arabic_processor.fix_arabic_text('التكلفة للطن'), f'${cost:.2f} ({local_cost:,.2f} {local_sym})']
        ]
        t = Table(tdata, colWidths=[250, 250])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), self.font_name),
            ('FONTSIZE', (0,0), (-1,-1), 11),
            ('BOTTOMPADDING', (0,0), (-1,0), 10),
            ('BACKGROUND', (0,1), (-1,-1), HexColor('#f5f5f5')),
            ('GRID', (0,0), (-1,-1), 1, HexColor('#2e7d32')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(t)
        story.append(Spacer(1, 20))

        story.append(p("المقادير المعتمدة لتركيب الطن الواحد:", size=14, color=HexColor('#2e7d32')))
        story.append(Spacer(1, 10))
        ing_data = [[arabic_processor.fix_arabic_text('المكون'), arabic_processor.fix_arabic_text('النسبة %'), arabic_processor.fix_arabic_text('كجم/طن')]]
        for ing, pct in formula.items():
            ing_data.append([arabic_processor.fix_arabic_text(ing), f'{pct:.2f}%', f'{pct*10:.1f}'])
        t2 = Table(ing_data, colWidths=[200, 150, 150])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor('#2e7d32')),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), self.font_name),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 1, HexColor('#bdbdbd')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [HexColor('#ffffff'), HexColor('#f5f5f5')]),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(t2)
        story.append(Spacer(1, 15))

        if include_charts and len(formula) > 1:
            try:
                fig, ax = plt.subplots(figsize=(6, 3.5))
                names = list(formula.keys())
                vals = list(formula.values())
                colors = ['#1b5e20','#2e7d32','#388e3c','#43a047','#4caf50','#66bb6a']
                ax.pie(vals, labels=None, autopct='%1.1f%%', colors=colors[:len(names)])
                ax.legend([arabic_processor.fix_arabic_text(n) for n in names], title=arabic_processor.fix_arabic_text("المكونات"),
                         loc='center left', bbox_to_anchor=(1,0,0.5,1), fontsize=8)
                ax.set_title(arabic_processor.fix_arabic_text('توزيع المكونات'), fontsize=12)
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
                plt.close()
                buf.seek(0)
                story.append(Image(buf, width=400, height=230))
            except:
                pass

        story.append(Spacer(1, 25))
        story.append(p("تم التوليد بواسطة منصة تاور العلمية © 2026 | تحت إشراف م. عبد القادر إسماعيل تاور", size=9, align=TA_CENTER, color=HexColor('#666666')))
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

pdf_generator = ProfessionalPDFGenerator()

# ==========================================
# 7. كلاس إدارة مزارع الدجاج اللاحم
# ==========================================
class BroilerFarmManager:
    @staticmethod
    def calculate_adg(current_weight_g: float, initial_weight_g: float, age_days: int) -> float:
        if age_days <= 0:
            return 0.0
        return (current_weight_g - initial_weight_g) / age_days

    @staticmethod
    def calculate_fcr(total_feed_kg: float, total_weight_gain_kg: float) -> float:
        if total_weight_gain_kg <= 0:
            return 0.0
        return total_feed_kg / total_weight_gain_kg

    @staticmethod
    def calculate_mortality_rate(dead_count: int, initial_count: int) -> float:
        if initial_count <= 0:
            return 0.0
        return (dead_count / initial_count) * 100.0

    @staticmethod
    def calculate_livability(initial_count: int, dead_count: int) -> float:
        return 100.0 - BroilerFarmManager.calculate_mortality_rate(dead_count, initial_count)

    @staticmethod
    def calculate_epef(livability: float, body_weight_kg: float, age_days: int, fcr: float) -> float:
        if age_days <= 0 or fcr <= 0:
            return 0.0
        return (livability * body_weight_kg) / (age_days * fcr) * 100.0

    @staticmethod
    def get_temp_humidity_table():
        data = {
            "العمر (يوم)": [1, 7, 14, 21, 28, 35, 42],
            "درجة الحرارة (مئوي)": [33, 30, 28, 26, 24, 22, 21],
            "الرطوبة النسبية (%)": [65, 65, 65, 60, 60, 55, 55]
        }
        return pd.DataFrame(data)

# ==========================================
# 8. مكتبة الأعلاف الكاملة
# ==========================================
BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة الكبرى": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0, "NDF": 9.5, "ADF": 3.2, "EE": 3.8, "ASH": 1.3},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0, "NDF": 10.2, "ADF": 3.5, "EE": 3.5, "ASH": 1.4},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0, "NDF": 18.5, "ADF": 7.5, "EE": 2.2, "ASH": 2.5},
        "سورجم (فتريتة)": {"CP": 10.0, "DC": 0.78, "SE": 70.0, "NDF": 12.5, "ADF": 5.5, "EE": 3.0, "ASH": 1.8},
        "قمح محلي مصنّع": {"CP": 12.0, "DC": 0.85, "SE": 75.0, "NDF": 11.5, "ADF": 3.8, "EE": 2.0, "ASH": 1.6}
    },
    "🌱 الأكساب وأمبازات مصادر البروتين العالي": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5, "EE": 1.5, "ASH": 5.5},
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0, "EE": 1.8, "ASH": 6.0},
        "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "SE": 76.0, "NDF": 12.0, "ADF": 7.0, "EE": 1.5, "ASH": 6.2}
    },
    "🚜 المخلفات الزراعية والصناعية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5, "EE": 3.5, "ASH": 5.5},
        "البرسيم الجاف (الدريس)": {"CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "ADF": 32.5, "EE": 2.0, "ASH": 10.5},
        "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8, "EE": 0.5, "ASH": 8.5}
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري (بودرة بلاط)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5},
        "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9},
        "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 85.0},
        "بيكربونات الصوديوم (الصودا)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0}
    }
}

# نظام أسعار المدن
CITY_PRICES_FILE = "city_prices.json"
def load_city_prices():
    if os.path.exists(CITY_PRICES_FILE):
        try:
            with open(CITY_PRICES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {}

CITY_CUSTOM_PRICES = load_city_prices()

class InventoryManager:
    @staticmethod
    def initialize_inventory():
        if "inventory" not in st.session_state:
            st.session_state["inventory"] = {}
            for cat_name, items in BIG_FEEDS_LIBRARY.items():
                for ing in items:
                    st.session_state["inventory"][ing] = {
                        "quantity": 25.0,
                        "min_threshold": 5.0,
                        "unit": "طن",
                        "last_updated": datetime.now().isoformat(),
                        "price_history": [],
                        "supplier": "غير محدد"
                    }

    @staticmethod
    def check_stock_levels() -> Dict[str, str]:
        warnings = {}
        for item, data in st.session_state["inventory"].items():
            qty = data["quantity"] if isinstance(data, dict) else data
            threshold = data["min_threshold"] if isinstance(data, dict) else 5.0
            if qty <= 0:
                warnings[item] = "نفذ المخزون"
            elif qty < threshold:
                warnings[item] = "منخفض"
        return warnings

InventoryManager.initialize_inventory()

EXCHANGE_RATES = {
    "السودان": {"rate": 600.0, "sym": "SDG", "currency_name": "جنيه سوداني"},
    "LIBYA": {"rate": 4.80, "sym": "LYD", "currency_name": "دينار ليبي"},
    "مصر": {"rate": 48.0, "sym": "EGP", "currency_name": "جنيه مصري"},
    "باقي دول العالم / البورصة المفتوحة": {"rate": 1.0, "sym": "USD", "currency_name": "دولار أمريكي"}
}

class MarketPriceEngine:
    @staticmethod
    @lru_cache(maxsize=128)
    def get_adjusted_market_data(country: str, state_or_region: str, city: str) -> Dict[str, float]:
        base_prices = {
            "ذرة صفراء": 230.0, "ذرة بيضاء": 225.0, "شعير مطحون": 210.0,
            "سورجم (فتريتة)": 195.0, "قمح محلي مصنّع": 240.0,
            "أمباز الفول السوداني (كسب)": 460.0, "كسب فول صويا 44%": 440.0,
            "كسب فول صويا 48%": 480.0,
            "نخالة قمح (ردة)": 150.0, "البرسيم الجاف (الدريس)": 170.0,
            "مولاس قصب السكر": 120.0,
            "الحجر الجيري (بودرة بلاط)": 40.0, "فوسفات ثنائي الكالسيوم (DCP)": 280.0,
            "ملح الطعام": 30.0, "مضاد سموم فطرية": 950.0,
            "بيكربونات الصوديوم (الصودا)": 340.0
        }
        multiplier = 1.0
        if country == "السودان":
            multiplier = 1.15
        elif country == "LIBYA":
            multiplier = 1.10
        elif country == "مصر":
            multiplier = 1.04
        
        for k in base_prices:
            base_prices[k] *= multiplier
        
        return base_prices

ANIMAL_IMAGES_RESOURCES = {
    "أبقار": "https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?q=80&w=600",
    "ماعز": "https://images.unsplash.com/photo-1524388680868-377a2e6bbb1c?q=80&w=600",
    "أغنام": "https://images.unsplash.com/photo-1484557985045-edf25e08da73?q=80&w=600",
    "خيول": "https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?q=80&w=600",
    "دواجن": "https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?q=80&w=600",
    "أسماك": "https://images.unsplash.com/photo-1522069169874-c58ec4b76be5?q=80&w=600",
    "سمان": "https://images.unsplash.com/photo-1516467508483-a7212febe31a?q=80&w=600",
    "عام": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600"
}

# ==========================================
# 9. حالة الجلسة
# ==========================================
if "approved" not in st.session_state: st.session_state["approved"] = False
if "user_role" not in st.session_state: st.session_state["user_role"] = None
if "login_welcome_shown" not in st.session_state: st.session_state["login_welcome_shown"] = False
if "login_attempts" not in st.session_state: st.session_state["login_attempts"] = 0
if "last_login_time" not in st.session_state: st.session_state["last_login_time"] = None
if "session_token" not in st.session_state: st.session_state["session_token"] = None
if "active_formula" not in st.session_state: st.session_state["active_formula"] = {"ذرة صفراء": 60.0, "كسب فول صويا 44%": 35.0}
if "active_cp_tag" not in st.session_state: st.session_state["active_cp_tag"] = 12.0
if "active_se_tag" not in st.session_state: st.session_state["active_se_tag"] = 65.0
if "active_breed_tag" not in st.session_state: st.session_state["active_breed_tag"] = "سلالة عامة"
if "active_animal_img" not in st.session_state: st.session_state["active_animal_img"] = ANIMAL_IMAGES_RESOURCES["عام"]
if "active_stage_title" not in st.session_state: st.session_state["active_stage_title"] = "إنتاج عام"
if "computed_ton_cost" not in st.session_state: st.session_state["computed_ton_cost"] = 280.0
if "broiler_farms" not in st.session_state: st.session_state["broiler_farms"] = {}
if "selected_farm" not in st.session_state: st.session_state["selected_farm"] = None

# ==========================================
# 10. CSS
# ==========================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=Tajawal:wght@400;500;700&display=swap');
    
    * {
        font-family: 'Cairo', 'Tajawal', sans-serif;
    }
    
    html, body, [data-testid="stAppViewContainer"] {
        background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    .stApp { 
        background: transparent; 
    }
    
    .main-box {
        background-color: rgba(255, 255, 255, 0.98);
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.18);
        margin-bottom: 50px;
        backdrop-filter: blur(10px);
    }
    
    h1, h2, h3, h4, h5, p, span, li { 
        font-family: 'Cairo', sans-serif; 
    }
    
    .formula-item {
        background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(232,245,233,0.9) 100%);
        padding: 15px 20px;
        border-radius: 12px;
        margin-bottom: 10px;
        font-weight: bold;
        color: #1b5e20 !important;
        border-right: 5px solid #2e7d32;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
        text-align: right;
        transition: transform 0.3s ease;
    }
    
    .formula-item:hover {
        transform: translateX(-5px);
        box-shadow: 0px 6px 20px rgba(0,0,0,0.15);
    }
    
    .section-title {
        color: #1b5e20;
        border-right: 6px solid #2e7d32;
        padding-right: 15px;
        text-align: right;
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 30px;
        margin-bottom: 20px;
        background: linear-gradient(to left, rgba(46,125,50,0.1), transparent);
        padding: 10px 15px;
        border-radius: 8px;
    }
    
    .price-card {
        background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
        padding: 20px;
        border-radius: 12px;
        border-right: 5px solid #2e7d32;
        margin-bottom: 20px;
        direction: rtl;
        text-align: right;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
    }
    
    .ai-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        margin: 10px 0;
    }
    
    .blockchain-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(240, 147, 251, 0.3);
        margin: 10px 0;
    }
    
    .iot-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(79, 172, 254, 0.3);
        margin: 10px 0;
    }
    
    .recommendation-card {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(67, 233, 123, 0.3);
        margin: 10px 0;
    }
    
    .analytics-card {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(250, 112, 154, 0.3);
        margin: 10px 0;
    }
    
    .glow-effect {
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from {
            box-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
        }
        to {
            box-shadow: 0 0 20px rgba(102, 126, 234, 0.8), 0 0 30px rgba(102, 126, 234, 0.6);
        }
    }
    
    .pulse-animation {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 11. بوابة الدخول
# ==========================================
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 300

if not st.session_state["approved"]:
    if st.session_state["login_attempts"] >= MAX_LOGIN_ATTEMPTS:
        if st.session_state["last_login_time"]:
            time_diff = (datetime.now() - st.session_state["last_login_time"]).seconds
            if time_diff < LOCKOUT_TIME:
                st.markdown('<div class="main-box" style="max-width: 500px; margin: 100px auto; direction: rtl;">', unsafe_allow_html=True)
                st.error(f"🔒 تم قفل النظام مؤقتاً. يرجى المحاولة بعد {LOCKOUT_TIME - time_diff} ثانية")
                st.markdown('</div>', unsafe_allow_html=True)
                st.stop()
            else:
                st.session_state["login_attempts"] = 0

    st.markdown('<div class="main-box" style="max-width: 500px; margin: 100px auto; direction: rtl;">', unsafe_allow_html=True)
    st.markdown("<h2 style='color: #2E7D32; text-align:center;'>🔒 بوابـة الدخـول الذكيـة</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#555;'>منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف</p>", unsafe_allow_html=True)

    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data("https://tower-scientific-platform.streamlit.app")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format="PNG")
        qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode()
        st.markdown(f'<div style="text-align:center; margin:20px 0;"><img src="data:image/png;base64,{qr_base64}" width="150"></div>', unsafe_allow_html=True)
    except:
        pass

    login_option = st.radio("طريقة الدخول:", ["كود الدخول السري", "اسم المستخدم وكلمة المرور"], horizontal=True)
    
    if login_option == "كود الدخول السري":
        input_code = st.text_input("🔑 أدخل كود الدخول الخاص بك:", type="password")
        col_login, col_reset = st.columns(2)
        with col_login:
            if st.button("تسجيل الدخول 🔓", type="primary", use_container_width=True):
                input_code_stripped = input_code.strip()
                if input_code_stripped in CODES_DB:
                    st.session_state["approved"] = True
                    st.session_state["user_role"] = CODES_DB[input_code_stripped]["role"]
                    st.session_state["login_welcome_shown"] = False
                    st.session_state["login_attempts"] = 0
                    st.session_state["last_login_time"] = datetime.now()
                    st.session_state["session_token"] = secrets.token_urlsafe(32)
                    st.rerun()
                else:
                    st.session_state["login_attempts"] += 1
                    st.session_state["last_login_time"] = datetime.now()
                    remaining = MAX_LOGIN_ATTEMPTS - st.session_state["login_attempts"]
                    st.error(f"❌ الكود غير صحيح! متبقي {remaining} محاولات")
        with col_reset:
            if st.button("🔄 نسيت الكود", use_container_width=True):
                st.info("يرجى التواصل مع مدير النظام: abukram128@gmail.com")
    else:
        username = st.text_input("👤 اسم المستخدم")
        password = st.text_input("🔑 كلمة المرور", type="password")
        if st.button("تسجيل الدخول 🔓", type="primary", use_container_width=True):
            auth = AuthManager()
            user = auth.authenticate(username, password)
            if user:
                st.session_state["approved"] = True
                st.session_state["user_role"] = user['role']
                st.session_state["login_welcome_shown"] = False
                st.session_state["login_attempts"] = 0
                st.session_state["last_login_time"] = datetime.now()
                st.session_state["session_token"] = secrets.token_urlsafe(32)
                st.session_state["user"] = user
                st.rerun()
            else:
                st.session_state["login_attempts"] += 1
                st.session_state["last_login_time"] = datetime.now()
                remaining = MAX_LOGIN_ATTEMPTS - st.session_state["login_attempts"]
                st.error(f"❌ اسم المستخدم أو كلمة المرور غير صحيحة! متبقي {remaining} محاولات")
        
        st.caption("💡 المستخدم الافتراضي: admin / admin123")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 12. الواجهة الرئيسية
# ==========================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)

col_logout_space, col_user_status = st.columns([0.7, 0.3])
with col_user_status:
    role_info = {"owner": "الاختصاصي م. عبد القادر إسماعيل تاور 👑", "specialist": "المختص والزملاء 👨‍🔬", "breeder": "المربي 🌾"}
    st.markdown(f"""<div style='text-align: left; font-size:0.9rem; color:#555; background: linear-gradient(135deg, #f5f5f5, #e0e0e0); padding: 10px; border-radius: 10px;'>الحساب: <b>{role_info.get(st.session_state["user_role"], "مستخدم")}</b><br><small>آخر دخول: {datetime.now().strftime('%Y-%m-%d %H:%M')}</small></div>""", unsafe_allow_html=True)
    if st.button("تسجيل الخروج 🚪", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key != "inventory":
                del st.session_state[key]
        st.session_state["approved"] = False
        st.session_state["user_role"] = None
        st.rerun()

col_logo, col_title = st.columns([0.3, 0.7])
with col_logo:
    if img_base64:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style pulse-animation" style="width:150px;height:150px;border-radius:50%;object-fit:cover;border:4px solid #d4af37;box-shadow:0px 6px 20px rgba(0,0,0,0.25);display:block;margin:0 auto;">', unsafe_allow_html=True)
    else:
        st.markdown(f'<img src="{ANIMAL_IMAGES_RESOURCES["عام"]}" class="profile-img-style pulse-animation" style="width:150px;height:150px;border-radius:50%;object-fit:cover;border:4px solid #d4af37;box-shadow:0px 6px 20px rgba(0,0,0,0.25);display:block;margin:0 auto;">', unsafe_allow_html=True)
with col_title:
    st.markdown("<h1 style='color: #1b5e20; text-align:right; margin-bottom:0;'>منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف 🌾</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #1565C0; text-align:right; font-size:1.2rem; margin-top:5px; margin-bottom:0;'>محرك الاستمثال الخطي المتقدم القائم على البروتين المهضوم (DP) ومعادل النشاء (SE)</p>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #c62828; text-align:right; font-weight: bold; margin-top: 5px;'>الاختصاصي م. عبد القادر إسماعيل تاور</h3>", unsafe_allow_html=True)

st.markdown("<hr style='border-top: 3px solid #2e7d32;'>", unsafe_allow_html=True)

# ==========================================
# 13. تحديد التبويبات
# ==========================================
# التأكد من وجود user_role قبل استخدامه
if st.session_state["user_role"] == "owner":
    tabs_titles = ["🔬 النمذجة والحسابات العلفية", "📊 بورصة الأسعار المركزية", "🏭 إدارة المستودعات الذكية", "🧾 التسويق وفواتير البيع", "📈 التحليلات المتقدمة", "🐔 إدارة مزارع الدجاج اللاحم", "💬 تعليقات المختصين", "📚 المراجع العلمية", "💡 المساعدة الذكية", "🤖 الذكاء الاصطناعي والتقنيات المتقدمة"]
elif st.session_state["user_role"] == "specialist":
    tabs_titles = ["🔬 النمذجة والحسابات العلفية", "📊 بورصة الأسعار المركزية", "🏭 إدارة المستودعات الذكية", "🧾 التسويق وفواتير البيع", "📈 التحليلات المتقدمة", "💬 تعليقات المختصين", "📚 المراجع العلمية", "💡 المساعدة الذكية"]
else:  # breeder
    tabs_titles = ["🔬 النمذجة والحسابات العلفية", "📚 المراجع العلمية", "💡 المساعدة الذكية"]

tabs = st.tabs(tabs_titles)

# ==========================================
# 14. التبويب الأول: النمذجة والحسابات العلفية
# ==========================================
with tabs[0]:
    sub_tab_formulator, sub_tab_analyzer = st.tabs(["🎯 تركيب علفة نموذجية", "🔬 مختبر تحليل الأعلاف"])

    with sub_tab_formulator:
        st.markdown('<div class="section-title">🌍 تحديد الموقع الجغرافي وبورصة الأسعار</div>', unsafe_allow_html=True)
        col_country, col_state, col_city = st.columns(3)
        with col_country:
            user_country = st.selectbox("اختر دولة المربي:", ["السودان", "LIBYA", "مصر", "باقي دول العالم / البورصة المفتوحة"])
        c_info = EXCHANGE_RATES.get(user_country, {"rate": 1.0, "sym": "USD", "currency_name": "دولار أمريكي"})
        local_rate = c_info["rate"]
        local_sym = c_info["sym"]

        with col_state:
            if user_country == "السودان":
                chosen_state = st.selectbox("اختر الولاية:", ["ولاية الخرطوم", "ولاية الجزيرة", "ولاية القضارف", "ولاية شمال كردفان", "ولاية جنوب كردفان", "ولاية غرب كردفان", "إقليم النيل الأزرق", "ولاية البحر الأحمر", "ولاية نهر النيل"])
            elif user_country == "LIBYA":
                chosen_state = st.selectbox("اختر الإقليم:", ["المنطقة الشرقية", "المنطقة الغربية", "المنطقة الجنوبية"])
            else:
                chosen_state = st.selectbox("الإقليم الإداري:", ["المركز الرئيسي العالمي", "الأسواق المفتوحة"])

        with col_city:
            if user_country == "السودان":
                cities_map = {
                    "ولاية الخرطوم": ["الخرطوم", "أم درمان", "بحري"],
                    "ولاية الجزيرة": ["ود مدني", "الحصاحيصا", "المناقل"],
                    "ولاية القضارف": ["القضارف المدينة", "الفاو"],
                    "ولاية شمال كردفان": ["الأبيض", "بارا", "أم روابة"],
                    "ولاية جنوب كردفان": ["كادوقلي", "الدلنج"],
                    "ولاية غرب كردفان": ["الفوله", "النهود", "بابنوسة"],
                    "إقليم النيل الأزرق": ["الدمازين", "الروصيرص"],
                    "ولاية البحر الأحمر": ["بورتسودان", "سواكن"],
                    "ولاية نهر النيل": ["شندي", "عطبرة", "الدامر"]
                }
                user_city = st.selectbox("اختر المدينة:", cities_map.get(chosen_state, ["عام"]))
            elif user_country == "LIBYA":
                cities_map = {
                    "المنطقة الشرقية": ["طبرق", "بنغازي", "البيضاء", "درنة"],
                    "المنطقة الغربية": ["طرابلس", "مصراتة", "الزاوية"],
                    "المنطقة الجنوبية": ["سبها", "مرزق", "غات"]
                }
                user_city = st.selectbox("اختر المدينة:", cities_map.get(chosen_state, ["عام"]))
            else:
                user_city = st.text_input("اكتب اسم المدينة:", "طبرق")

        city_key = f"{user_country}|||{chosen_state}|||{user_city}"
        custom_prices = CITY_CUSTOM_PRICES.get(city_key, {})
        live_prices = MarketPriceEngine.get_adjusted_market_data(user_country, chosen_state, user_city)

        # اختيار القطاع والإنتاج
        st.markdown('<div class="section-title">⚖️ اختيار القطاع والنوع والإنتاجية المستهدفة</div>', unsafe_allow_html=True)
        col_sec, col_sub, col_prod = st.columns(3)
        with col_sec:
            main_sector = st.selectbox("اختر القطاع الإنتاجي:", ["الأغنام وسلالاتها 🐏", "الماعز وسلالاتها", "الأبقار وسلالاتها", "الخيول والفروسية", "الطيور والسمان", "الأسماك والأحياء المائية"])
        
        dynamic_img_key = "عام"
        default_dp = 11.0
        default_se = 60.0
        
        with col_sub:
            if main_sector == "الأغنام وسلالاتها 🐏":
                sub_type = st.selectbox("السلالة:", ["الضأن الصحراوي السوداني", "البربري", "النعيمي", "سلالات محلية / هجين"])
                dynamic_img_key = "أغنام"
            elif main_sector == "الماعز وسلالاتها":
                sub_type = st.selectbox("السلالة:", ["الماعز النوبي السوداني", "الماعز الصحراوي", "بور / محسن"])
                dynamic_img_key = "ماعز"
            elif main_sector == "الأبقار وسلالاتها":
                sub_type = st.selectbox("السلالة:", ["كنانة (سوداني)", "بطانة (مدر)", "هولشتاين / محسن"])
                dynamic_img_key = "أبقار"
            elif main_sector == "الخيول والفروسية":
                sub_type = st.selectbox("السلالة:", ["خيل عربي أصيل", "ثوروبريد", "خيول محلية هجين"])
                dynamic_img_key = "خيول"
            elif main_sector == "الطيور والسمان":
                sub_type = st.selectbox("نوع الطيور:", ["طائر السمان (Quail)", "دواجن لاحم (Broiler)", "دواجن بياض (Layer)"])
                dynamic_img_key = "سمان" if "السمان" in sub_type else "دواجن"
            else:
                sub_type = st.selectbox("نوع الأسماك:", ["البلطي النيلي (Tilapia)", "القرموط"])
                dynamic_img_key = "أسماك"

        with col_prod:
            if main_sector == "الطيور والسمان":
                if "السمان" in sub_type:
                    prod_stage = st.selectbox("نوع الإنتاج:", ["سمان بادي / نامي", "سمان بياض إنتاجي"])
                    default_dp = 20.0 if "بادي" in prod_stage else 16.5
                    default_se = 72.0 if "بادي" in prod_stage else 68.0
                else:
                    prod_stage = st.selectbox("نوع الإنتاج:", ["بادي دواجن 23%", "نامي دواجن 21%", "ناهي دواجن 19%", "بياض إنتاجي"])
                    default_dp = 20.0 if "بادي" in prod_stage else (18.5 if "نامي" in prod_stage else (16.5 if "ناهي" in prod_stage else 15.0))
                    default_se = 76.0 if "بادي" in prod_stage else (74.0 if "نامي" in prod_stage else (75.0 if "ناهي" in prod_stage else 70.0))
            else:
                prod_stage = st.selectbox("نوع الإنتاج:", ["تسمين مكثف", "إنتاج حليب", "صيانة"])
                default_dp = 12.0 if "تسمين" in prod_stage else (14.0 if "حليب" in prod_stage else 9.0)
                default_se = 65.0 if "تسمين" in prod_stage else (68.0 if "حليب" in prod_stage else 55.0)

        # حدود الموازنة
        st.markdown('<div class="section-title">📋 حدود الموازنة الذكية (DP & SE)</div>', unsafe_allow_html=True)
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.metric("🧬 بروتين مهضوم (DP) مقترح:", f"{default_dp} %")
            final_target_dp = st.slider("حدّد نسبة DP:", 5.0, 40.0, value=default_dp)
        with col_p2:
            st.metric("🌽 معادل النشاء (SE) مقترح:", f"{default_se} وحدة")
            final_target_se = st.slider("حدّد حد الـ SE المستهدف:", 10.0, 90.0, value=default_se)

        # اختيار المكونات
        selected_ingredients = []
        ingredient_prices = {}
        for cat_name, items in BIG_FEEDS_LIBRARY.items():
            with st.expander(f"📁 {cat_name}", expanded=True if "الحبوب" in cat_name or "الأكساب" in cat_name else False):
                sub_cols = st.columns(3)
                for idx, (ing_name, _) in enumerate(items.items()):
                    with sub_cols[idx % 3]:
                        is_def = ing_name in ["ذرة صفراء", "كسب فول صويا 44%", "نخالة قمح (ردة)", "ملح الطعام", "الحجر الجيري (بودرة بلاط)", "فوسفات ثنائي الكالسيوم (DCP)", "مضاد سموم فطرية"]
                        checked = st.checkbox(ing_name, value=is_def, key=f"feed_{ing_name}")
                        current_live_price = live_prices.get(ing_name, 350.0)
                        if ing_name in custom_prices:
                            current_live_price = custom_prices[ing_name]
                        price_input = st.number_input(f"السعر للطن ({ing_name}) $:", min_value=5.0, value=float(current_live_price), key=f"price_{ing_name}")
                        if checked:
                            selected_ingredients.append(ing_name)
                            ingredient_prices[ing_name] = price_input

        # الإضافات التلقائية
        fixed_additives = {"ملح الطعام": 0.5, "مضاد سموم فطرية": 0.2, "الحجر الجيري (بودرة بلاط)": 1.5, "فوسفات ثنائي الكالسيوم (DCP)": 1.0}
        
        for item, pct in fixed_additives.items():
            if item not in selected_ingredients:
                selected_ingredients.append(item)
                ingredient_prices[item] = live_prices.get(item, 40.0)

        # زر تشغيل المحرك
        if st.button("🚀 تشغيل محرك الاستمثال الخطي", type="primary", use_container_width=True):
            if len(selected_ingredients) < 2:
                st.error("❌ الرجاء اختيار مكونين على الأقل!")
            else:
                c_vector = [ingredient_prices[ing] for ing in selected_ingredients]
                bounds = [(fixed_additives[ing], fixed_additives[ing]) if ing in fixed_additives else (0.0, 100.0) for ing in selected_ingredients]

                A_eq = [[1.0 for _ in selected_ingredients]]
                b_eq = [100.0]

                dp_row = []
                se_row = []
                for ing in selected_ingredients:
                    cp_val = 0.0
                    dc_val = 0.0
                    se_val = 0.0
                    for cat in BIG_FEEDS_LIBRARY.values():
                        if ing in cat:
                            cp_val = cat[ing].get("CP", 0.0)
                            dc_val = cat[ing].get("DC", 0.0)
                            se_val = cat[ing].get("SE", 0.0)
                    dp_row.append(cp_val * dc_val)
                    se_row.append(se_val)
                A_eq.append(dp_row)
                b_eq.append(final_target_dp * 100.0)

                A_ub = []
                b_ub = []
                A_ub.append([-1.0 * x for x in se_row])
                b_ub.append(-1.0 * final_target_se * 100.0)

                grain_indicators = [1.0 if ing in BIG_FEEDS_LIBRARY["🌾 الحبوب ومصادر الطاقة الكبرى"] else 0.0 for ing in selected_ingredients]
                if sum(grain_indicators) > 0:
                    A_ub.append([-1.0 * x for x in grain_indicators])
                    b_ub.append(-50.0)

                if "نخالة قمح (ردة)" in selected_ingredients:
                    fiber_indicators = [1.0 if ing == "نخالة قمح (ردة)" else 0.0 for ing in selected_ingredients]
                    A_ub.append(fiber_indicators)
                    b_ub.append(18.0)

                res = linprog(c_vector, A_ub=A_ub if A_ub else None, b_ub=b_ub if b_ub else None, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
                
                if not res.success:
                    # محاولة مرنة
                    A_ub_flex = []
                    b_ub_flex = []
                    A_ub_flex.append([-1.0 * x for x in se_row])
                    b_ub_flex.append(-1.0 * (final_target_se - 3.0) * 100.0)
                    if sum(grain_indicators) > 0:
                        A_ub_flex.append([-1.0 * x for x in grain_indicators])
                        b_ub_flex.append(-40.0)
                    res = linprog(c_vector, A_ub=A_ub_flex, b_ub=b_ub_flex, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

                if res.success:
                    formula_results = {}
                    computed_se_total = 0.0
                    for idx, ing in enumerate(selected_ingredients):
                        if res.x[idx] > 0.0001:
                            formula_results[ing] = res.x[idx]
                            for cat in BIG_FEEDS_LIBRARY.values():
                                if ing in cat:
                                    computed_se_total += (res.x[idx] / 100.0) * cat[ing].get("SE", 0.0)

                    st.session_state["active_formula"] = formula_results
                    st.session_state["active_cp_tag"] = final_target_dp
                    st.session_state["active_se_tag"] = computed_se_total
                    st.session_state["active_breed_tag"] = sub_type
                    st.session_state["active_animal_img"] = ANIMAL_IMAGES_RESOURCES.get(dynamic_img_key, ANIMAL_IMAGES_RESOURCES["عام"])
                    st.session_state["active_stage_title"] = f"{main_sector} - {prod_stage}"
                    st.success(f"🎯 تم تشغيل محرك الاستمثال الخطي بنجاح في سوق: {user_city}")

                    res_col1, res_col2 = st.columns([0.6, 0.4])
                    with res_col1:
                        st.write("#### 📝 المقادير المعتمدة لتركيب طن واحد (كجم):")
                        for k, v in formula_results.items():
                            st.markdown(f'<div class="formula-item">▪️ <b>{k}:</b> {v:.2f} % ➡️ ({v*10:.1f} كجم / طن)</div>', unsafe_allow_html=True)

                        ton_cost = res.fun / 100.0 if hasattr(res, 'fun') else 280.0
                        st.session_state["computed_ton_cost"] = ton_cost
                        st.metric(f"💰 التكلفة الفعلية لإنتاج الطن في {user_city}: ", f"${ton_cost:.2f} (أو {ton_cost*local_rate:,.1f} {local_sym})")

                        # إضافة توثيق Blockchain
                        blockchain = ADVANCED_SYSTEMS['blockchain']
                        transaction = blockchain.add_transaction(
                            sender="Tower_Platform",
                            receiver=user_city,
                            data={
                                "formula": {k: round(v, 2) for k, v in formula_results.items()},
                                "cost": round(ton_cost, 2),
                                "dp": round(final_target_dp, 2),
                                "se": round(computed_se_total, 2),
                                "timestamp": datetime.now().isoformat()
                            }
                        )
                        if len(blockchain.pending_transactions) >= 3:
                            block = blockchain.mine_block()
                            if block:
                                st.success(f"⛓️ تم توثيق المعاملة في Blockchain (كتلة #{block['index']})")

                    with res_col2:
                        fig = px.pie(values=list(formula_results.values()), names=list(formula_results.keys()), title="توزيع مكونات الخلطة", color_discrete_sequence=px.colors.sequential.Greens)
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                        chart_data = pd.DataFrame({'المكون': list(formula_results.keys()), 'النسبة المئوية': list(formula_results.values()), 'الوزن (كجم/طن)': [v*10 for v in formula_results.values()]})
                        st.bar_chart(chart_data.set_index('المكون')['الوزن (كجم/طن)'])
                else:
                    st.error("❌ تعذر إيجاد حل رياضي متزن. يرجى إتاحة خامات إضافية لتوسيع مساحة الحل.")

    with sub_tab_analyzer:
        st.markdown('<div class="section-title">🔬 مختبر فحص وتحليل الخلطات الجاهزة</div>', unsafe_allow_html=True)
        st.write("اكتب مقادير خلطتك الحالية بالكيلوجرام، وسيقوم المختبر بتحليلها برمجياً.")
        
        lab_user_inputs = {}
        all_library_ingredients = []
        for cat_name, items in BIG_FEEDS_LIBRARY.items():
            for ing_name in items.keys():
                all_library_ingredients.append(ing_name)

        col_input1, col_input2, col_input3 = st.columns(3)
        total_ing_count = len(all_library_ingredients)
        segment = total_ing_count // 3 + 1
        with col_input1:
            for ing_name in all_library_ingredients[:segment]:
                lab_user_inputs[ing_name] = st.number_input(f"وزن {ing_name} (كجم):", min_value=0.0, value=0.0, step=5.0, key=f"lab_{ing_name}")
        with col_input2:
            for ing_name in all_library_ingredients[segment:segment*2]:
                lab_user_inputs[ing_name] = st.number_input(f"وزن {ing_name} (كجم):", min_value=0.0, value=0.0, step=5.0, key=f"lab_{ing_name}")
        with col_input3:
            for ing_name in all_library_ingredients[segment*2:]:
                lab_user_inputs[ing_name] = st.number_input(f"وزن {ing_name} (كجم):", min_value=0.0, value=0.0, step=5.0, key=f"lab_{ing_name}")

        if st.button("🧪 تشغيل التحليل المخبري", type="primary", use_container_width=True):
            lab_total_weight = sum(lab_user_inputs.values())
            if lab_total_weight <= 0:
                st.warning("⚠️ الرجاء إدخال أوزان أكبر من الصفر.")
            else:
                calculated_total_dp = 0.0
                calculated_total_se = 0.0
                for ing_name, weight in lab_user_inputs.items():
                    if weight > 0:
                        pct = weight / lab_total_weight
                        ing_cp = 0.0
                        ing_dc = 0.0
                        ing_se = 0.0
                        for cat, items in BIG_FEEDS_LIBRARY.items():
                            if ing_name in items:
                                ing_cp = items[ing_name].get("CP", 0.0)
                                ing_dc = items[ing_name].get("DC", 0.0)
                                ing_se = items[ing_name].get("SE", 0.0)
                        calculated_total_dp += pct * (ing_cp * ing_dc)
                        calculated_total_se += pct * ing_se

                st.success("🔬 تم فحص العينة وتحليل المحتوى الغذائي بنجاح!")
                st.metric("البروتين المهضوم (DP) المحسوب:", f"{calculated_total_dp:.2f}%")
                st.metric("معادل النشاء (SE) المحسوب:", f"{calculated_total_se:.2f} وحدة")

# ==========================================
# 15. تبويب الذكاء الاصطناعي والتقنيات المتقدمة (للمالك فقط)
# ==========================================
if st.session_state["user_role"] == "owner":
    advanced_tab_index = 9  # التبويب الأخير
    with tabs[advanced_tab_index]:
        st.markdown('<div class="section-title">🤖 لوحة التحكم بالذكاء الاصطناعي والتقنيات المتقدمة</div>', unsafe_allow_html=True)
        
        adv_tabs = st.tabs([
            "🧠 التنبؤات الذكية",
            "⛓️ توثيق Blockchain",
            "📡 محاكي IoT",
            "💡 التوصيات الذكية",
            "📊 التحليلات ثلاثية الأبعاد"
        ])
        
        # التبويب الفرعي 1: التنبؤات الذكية
        with adv_tabs[0]:
            st.markdown('<div class="ai-card"><h3>🧠 نظام التنبؤات بالذكاء الاصطناعي</h3></div>', unsafe_allow_html=True)
            
            col_pred1, col_pred2 = st.columns(2)
            
            with col_pred1:
                st.subheader("📈 تنبؤات الأسعار المتقدمة")
                ingredient_for_prediction = st.selectbox(
                    "اختر المادة الخام:",
                    ["ذرة صفراء", "كسب فول صويا 44%", "نخالة قمح", "شعير مطحون"]
                )
                prediction_days = st.slider("عدد أيام التنبؤ:", 1, 30, 7)
                
                if st.button("🔮 تشغيل التنبؤ المتقدم", type="primary", use_container_width=True):
                    with st.spinner("جاري تحليل البيانات وتشغيل نماذج الذكاء الاصطناعي..."):
                        historical_data = np.random.normal(250, 20, 30) + np.linspace(0, 30, 30)
                        ai_model = ADVANCED_SYSTEMS['ai_model']
                        result = ai_model.predict_with_confidence(historical_data, prediction_days)
                        
                        st.success("✅ تم الانتهاء من التحليل!")
                        
                        col_metric1, col_metric2, col_metric3 = st.columns(3)
                        with col_metric1:
                            st.metric("السعر المتوقع", f"${result['predictions'][-1]:.2f}")
                        with col_metric2:
                            trend_emoji = "📈" if result['trend']['trend'] == 'up' else "📉" if result['trend']['trend'] == 'down' else "➡️"
                            st.metric("الاتجاه", result['trend']['trend'], delta=trend_emoji)
                        with col_metric3:
                            st.metric("مستوى الثقة", f"{result['confidence']*100:.1f}%")
                        
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(y=historical_data, mode='lines+markers', name='البيانات التاريخية', line=dict(color='#2e7d32', width=2)))
                        future_x = list(range(len(historical_data), len(historical_data) + prediction_days))
                        fig.add_trace(go.Scatter(x=future_x, y=result['predictions'], mode='lines+markers', name='التنبؤ', line=dict(color='#ff6f00', width=2, dash='dash')))
                        fig.update_layout(title=f'تحليل اتجاه سعر {ingredient_for_prediction}', xaxis_title='الفترة الزمنية', yaxis_title='السعر ($)', template='plotly_white')
                        st.plotly_chart(fig, use_container_width=True)
            
            with col_pred2:
                st.subheader("📊 تحليل الأداء الإنتاجي")
                performance_data = pd.DataFrame({
                    'العمر (يوم)': range(1, 43),
                    'الوزن (كجم)': [0.045 + i * 0.065 + np.random.normal(0, 0.01) for i in range(42)],
                    'FCR': [2.0 - i * 0.01 + np.random.normal(0, 0.05) for i in range(42)]
                })
                
                fig = make_subplots(rows=2, cols=1, subplot_titles=('الوزن (كجم)', 'معامل التحويل FCR'), shared_xaxes=True)
                fig.add_trace(go.Scatter(x=performance_data['العمر (يوم)'], y=performance_data['الوزن (كجم)'], mode='lines', name='الوزن', line=dict(color='#2e7d32')), row=1, col=1)
                fig.add_trace(go.Scatter(x=performance_data['العمر (يوم)'], y=performance_data['FCR'], mode='lines', name='FCR', line=dict(color='#c62828')), row=2, col=1)
                fig.update_layout(height=500, template='plotly_white')
                st.plotly_chart(fig, use_container_width=True)
        
        # التبويب الفرعي 2: Blockchain
        with adv_tabs[1]:
            st.markdown('<div class="blockchain-card"><h3>⛓️ نظام توثيق المعاملات بتقنية Blockchain</h3></div>', unsafe_allow_html=True)
            
            blockchain = ADVANCED_SYSTEMS['blockchain']
            
            col_block1, col_block2 = st.columns(2)
            
            with col_block1:
                st.subheader("📝 إضافة معاملة جديدة")
                tx_data = st.text_area("بيانات المعاملة (JSON):", 
                                      value=json.dumps({"type": "feed_sale", "customer": "مزرعة النور", "quantity": 5, "unit": "طن", "price": 1500}, indent=2))
                
                if st.button("➕ إضافة معاملة إلى السلسلة", type="primary", use_container_width=True):
                    try:
                        data_dict = json.loads(tx_data)
                        transaction = blockchain.add_transaction("Tower_Platform", "Customer_Wallet", data_dict)
                        st.success(f"✅ تمت إضافة المعاملة بنجاح!")
                        st.json(transaction)
                        
                        if len(blockchain.pending_transactions) >= 3:
                            block = blockchain.mine_block()
                            if block:
                                st.success(f"⛏️ تم تعدين كتلة جديدة! رقم الكتلة: {block['index']}")
                    except Exception as e:
                        st.error(f"❌ خطأ: {e}")
            
            with col_block2:
                st.subheader("📊 حالة سلسلة الكتل")
                col_stats1, col_stats2, col_stats3 = st.columns(3)
                with col_stats1:
                    st.metric("عدد الكتل", len(blockchain.chain))
                with col_stats2:
                    st.metric("المعاملات المعلقة", len(blockchain.pending_transactions))
                with col_stats3:
                    chain_valid = blockchain.verify_chain()
                    st.metric("سلامة السلسلة", "✅ صالحة" if chain_valid else "❌ مخترقة")
                
                st.subheader("📦 آخر الكتل")
                for block in blockchain.chain[-3:]:
                    with st.expander(f"كتلة #{block['index']} - {block['timestamp'][:16]}"):
                        st.json({
                            'index': block['index'],
                            'hash': block['hash'][:20] + '...',
                            'previous_hash': block['previous_hash'][:20] + '...',
                            'transactions_count': len(block['transactions'])
                        })
        
        # التبويب الفرعي 3: IoT
        with adv_tabs[2]:
            st.markdown('<div class="iot-card"><h3>📡 محاكي إنترنت الأشياء (IoT) للمزرعة الذكية</h3></div>', unsafe_allow_html=True)
            
            iot = ADVANCED_SYSTEMS['iot_simulator']
            
            col_iot1, col_iot2 = st.columns(2)
            
            with col_iot1:
                st.subheader("🌡️ قراءات المستشعرات الحية")
                
                if st.button("📡 قراءة المستشعرات الآن", type="primary", use_container_width=True):
                    readings = iot.read_sensors()
                    
                    for sensor, data in readings.items():
                        col_sensor1, col_sensor2 = st.columns([0.7, 0.3])
                        with col_sensor1:
                            st.metric(f"{sensor.replace('_', ' ').title()}", f"{data['value']:.2f} {data['unit']}", delta=data['status'])
                        with col_sensor2:
                            if data['status'] == 'warning':
                                st.warning("⚠️")
                            else:
                                st.success("✅")
                    
                    anomalies = iot.detect_anomalies(readings)
                    if anomalies:
                        st.warning("🚨 تم اكتشاف قراءات شاذة!")
                        for anomaly in anomalies:
                            st.error(f"**{anomaly['sensor']}**: القيمة: {anomaly['value']:.2f} | المتوقع: {anomaly['expected']:.2f} | الشدة: {anomaly['severity']}")
            
            with col_iot2:
                st.subheader("📈 البيانات التاريخية للمستشعرات")
                historical_iot = pd.DataFrame({
                    'الوقت': pd.date_range(start='2024-01-01', periods=100, freq='H'),
                    'درجة الحرارة': 25 + np.random.normal(0, 2, 100) + 5 * np.sin(np.linspace(0, 4*np.pi, 100)),
                    'الرطوبة': 60 + np.random.normal(0, 5, 100)
                })
                
                fig = go.Figure()
                for col in ['درجة الحرارة', 'الرطوبة']:
                    fig.add_trace(go.Scatter(x=historical_iot['الوقت'], y=historical_iot[col], mode='lines', name=col))
                fig.update_layout(title='قراءات المستشعرات التاريخية', xaxis_title='الوقت', yaxis_title='القيمة', template='plotly_dark', height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        # التبويب الفرعي 4: التوصيات الذكية
        with adv_tabs[3]:
            st.markdown('<div class="recommendation-card"><h3>💡 نظام التوصيات الذكي</h3></div>', unsafe_allow_html=True)
            
            rec_system = ADVANCED_SYSTEMS['recommendation_system']
            
            col_rec1, col_rec2 = st.columns(2)
            
            with col_rec1:
                st.subheader("🎯 توصيات التركيبة المثلى")
                animal_type = st.selectbox("نوع الحيوان:", ["دواجن لاحم", "أبقار حلوب", "أغنام تسمين"])
                
                current_prices = {'ذرة صفراء': 250, 'كسب فول صويا 44%': 450, 'نخالة قمح': 160, 'شعير مطحون': 220}
                
                if st.button("🔍 تحليل وتوصيات", type="primary", use_container_width=True):
                    recommendations = rec_system.get_optimal_formula_recommendation(animal_type, 2.0, current_prices)
                    
                    if recommendations['cost_optimization']:
                        st.success("💡 توصيات تحسين التكلفة:")
                        for rec in recommendations['cost_optimization']:
                            st.info(f"**{rec['ingredient']}** (السعر الحالي: ${rec['current_price']})")
                            for alt in rec['alternatives']:
                                st.markdown(f"- {alt['name']}: ${alt['price']} (توفير: ${alt['savings']:.2f} - {alt['savings_percent']:.1f}%)")
                    
                    if recommendations['seasonal_recommendations']:
                        st.warning("🌡️ توصيات موسمية:")
                        for rec in recommendations['seasonal_recommendations']:
                            st.markdown(f"**{rec['type']}:**")
                            for action in rec['actions']:
                                st.markdown(f"- {action}")
            
            with col_rec2:
                st.subheader("📊 تحليل الأداء المتوقع")
                
                if st.button("📈 توقع الأداء", type="primary", use_container_width=True):
                    categories = ['معدل النمو', 'كفاءة التحويل', 'الصحة', 'التكلفة', 'الجودة']
                    values = [85, 78, 92, 70, 88]
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself', name='الأداء المتوقع'))
                    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=True, title='تحليل الأداء المتوقع للتركيبة')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    col_perf1, col_perf2, col_perf3 = st.columns(3)
                    with col_perf1: st.metric("توفير التكلفة", "15%", delta="+5%")
                    with col_perf2: st.metric("تحسين FCR", "1.65", delta="-0.15")
                    with col_perf3: st.metric("معدل النمو", "58 جم/يوم", delta="+3 جم")
        
        # التبويب الفرعي 5: التحليلات ثلاثية الأبعاد
        with adv_tabs[4]:
            st.markdown('<div class="analytics-card"><h3>📊 التحليلات المتقدمة والتصورات ثلاثية الأبعاد</h3></div>', unsafe_allow_html=True)
            
            analytics = ADVANCED_SYSTEMS['advanced_analytics']
            
            col_3d1, col_3d2 = st.columns(2)
            
            with col_3d1:
                st.subheader("🔬 تحليل ثلاثي الأبعاد للأداء")
                np.random.seed(42)
                df_3d = pd.DataFrame({
                    'الوزن': np.random.normal(2.5, 0.5, 100),
                    'العمر': np.random.normal(35, 5, 100),
                    'FCR': np.random.normal(1.7, 0.2, 100),
                    'التكلفة': np.random.normal(300, 50, 100)
                })
                
                fig_3d = analytics.create_3d_visualization(df_3d, x_col='الوزن', y_col='العمر', z_col='FCR', color_col='التكلفة')
                st.plotly_chart(fig_3d, use_container_width=True)
            
            with col_3d2:
                st.subheader("🔥 خريطة حرارية للارتباطات")
                correlation_data = pd.DataFrame({
                    'الوزن': [1.0, 0.8, -0.6, 0.3],
                    'العمر': [0.8, 1.0, -0.4, 0.2],
                    'FCR': [-0.6, -0.4, 1.0, -0.5],
                    'التكلفة': [0.3, 0.2, -0.5, 1.0]
                }, index=['الوزن', 'العمر', 'FCR', 'التكلفة'])
                
                fig_heatmap = analytics.generate_heatmap_analysis(correlation_data)
                st.plotly_chart(fig_heatmap, use_container_width=True)

# شريط جانبي للأنظمة المتقدمة (للمالك فقط)
if st.session_state["user_role"] == "owner":
    with st.sidebar:
        st.markdown("### 🤖 الأنظمة المتقدمة النشطة")
        
        col_status1, col_status2 = st.columns(2)
        with col_status1:
            st.markdown("🧠 **AI**: <span style='color: #4CAF50;'>● نشط</span>", unsafe_allow_html=True)
            st.markdown("⛓️ **Blockchain**: <span style='color: #4CAF50;'>● نشط</span>", unsafe_allow_html=True)
        with col_status2:
            st.markdown("📡 **IoT**: <span style='color: #4CAF50;'>● نشط</span>", unsafe_allow_html=True)
            st.markdown("💡 **Recommendation**: <span style='color: #4CAF50;'>● نشط</span>", unsafe_allow_html=True)
        
        st.markdown("---")
        blockchain = ADVANCED_SYSTEMS['blockchain']
        st.metric("المعاملات المؤمنة", len(blockchain.chain))
        st.metric("قراءات IoT اليوم", len(ADVANCED_SYSTEMS['iot_simulator'].data_stream))

st.markdown('</div>', unsafe_allow_html=True)

# تذييل المنصة
st.markdown("""
<div style='position: fixed; bottom: 20px; right: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
     padding: 10px 20px; border-radius: 25px; color: white; font-size: 0.8rem; z-index: 9999; 
     box-shadow: 0 4px 15px rgba(0,0,0,0.2);'>
    🤖 Powered by Advanced AI & Blockchain Technology
</div>
""", unsafe_allow_html=True)
