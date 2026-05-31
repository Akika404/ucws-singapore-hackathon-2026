import type { Lang } from './index'

/**
 * 跨端关键数据：行业大类（国民经济行业分类 A~T）。
 * 注意：英文版必须与后端 server/services/prompts.py 的 INDUSTRY_CATEGORIES['en'] 逐字一致，
 * 因为前端把所选行业字符串发给后端、并用后端返回值匹配本列表。稳定锚点是 (A)~(T) 字母前缀。
 * 中文版必须与后端 INDUSTRY_CATEGORIES['zh'] 一致。
 */
export const INDUSTRIES: Record<Lang, string[]> = {
  zh: [
    '(A) 农、林、牧、渔业', '(B) 采矿业', '(C) 制造业',
    '(D) 电力、热力、燃气及水生产和供应业', '(E) 建筑业',
    '(F) 批发和零售业', '(G) 交通运输、仓储和邮政业',
    '(H) 住宿和餐饮业', '(I) 信息传输、软件和信息技术服务业',
    '(J) 金融业', '(K) 房地产业', '(L) 租赁和商务服务业',
    '(M) 科学研究和技术服务业', '(N) 水利、环境和公共设施管理业',
    '(O) 居民服务、修理和其他服务业', '(P) 教育',
    '(Q) 卫生和社会工作', '(R) 文化、体育和娱乐业',
    '(S) 公共管理、社会保障和社会组织', '(T) 国际组织',
  ],
  en: [
    '(A) Agriculture, Forestry, Animal Husbandry and Fishery', '(B) Mining', '(C) Manufacturing',
    '(D) Production and Supply of Electricity, Heat, Gas and Water', '(E) Construction',
    '(F) Wholesale and Retail Trade', '(G) Transportation, Storage and Postal Services',
    '(H) Accommodation and Catering', '(I) Information Transmission, Software and IT Services',
    '(J) Finance', '(K) Real Estate', '(L) Leasing and Business Services',
    '(M) Scientific Research and Technical Services', '(N) Water Conservancy, Environment and Public Facilities Management',
    '(O) Residential Services, Repair and Other Services', '(P) Education',
    '(Q) Health and Social Work', '(R) Culture, Sports and Entertainment',
    '(S) Public Administration, Social Security and Social Organizations', '(T) International Organizations',
  ],
}

/** StepPage 注册地址省份列表（31 项）。值会发给后端 page6，仅作展示与回显，可整列本地化。 */
export const PROVINCES_FULL: Record<Lang, string[]> = {
  zh: [
    '北京市', '天津市', '河北省', '山西省', '内蒙古自治区',
    '辽宁省', '吉林省', '黑龙江省', '上海市', '江苏省',
    '浙江省', '安徽省', '福建省', '江西省', '山东省',
    '河南省', '湖北省', '湖南省', '广东省', '广西壮族自治区',
    '海南省', '重庆市', '四川省', '贵州省', '云南省',
    '西藏自治区', '陕西省', '甘肃省', '青海省', '宁夏回族自治区',
    '新疆维吾尔自治区',
  ],
  en: [
    'Beijing', 'Tianjin', 'Hebei', 'Shanxi', 'Inner Mongolia',
    'Liaoning', 'Jilin', 'Heilongjiang', 'Shanghai', 'Jiangsu',
    'Zhejiang', 'Anhui', 'Fujian', 'Jiangxi', 'Shandong',
    'Henan', 'Hubei', 'Hunan', 'Guangdong', 'Guangxi',
    'Hainan', 'Chongqing', 'Sichuan', 'Guizhou', 'Yunnan',
    'Tibet', 'Shaanxi', 'Gansu', 'Qinghai', 'Ningxia',
    'Xinjiang',
  ],
}
