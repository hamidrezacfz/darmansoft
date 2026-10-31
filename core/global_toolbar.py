from django.utils import timezone
from django.utils.html import escape


class GlobalToolbarMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if 'text/html' not in response.get('Content-Type', '') or not hasattr(response, 'content'):
            return response
        user = getattr(request, 'user', None)
        username = user.get_username() if user and user.is_authenticated else 'مهمان'
        stamp = timezone.localtime().strftime('%Y/%m/%d - %H:%M')
        toolbar = f'''<div class="darman-global-toolbar"><a href="/">صفحه اصلی</a><a href="/laboratory/">کارتابل آزمایشگاه</a><span>تاریخ و ساعت سیستم: {escape(stamp)}</span><span>کاربر: {escape(username)}</span></div><style>.darman-global-toolbar{{position:fixed;z-index:9999;bottom:0;right:0;left:0;display:flex;justify-content:center;gap:20px;padding:7px 12px;background:#18323a;color:#fff;font:11px Tahoma;box-shadow:0 -2px 8px #0002}}.darman-global-toolbar a{{color:#bde8dc;text-decoration:none;font-weight:bold}}body{{font-family:Tahoma,Arial,sans-serif!important;background:#f3f7f8!important}}button,input,select,textarea{{font-family:Tahoma,Arial,sans-serif!important}}.hero a{{display:none!important}}.box,.card,.panel,.list{{box-shadow:0 8px 24px #18323a0d;border-radius:16px}}.grid,.layout{{grid-template-columns:minmax(360px,1fr) minmax(360px,1fr)!important;align-items:start!important;gap:18px!important}}.wrap,.app{{max-width:1280px!important;padding:22px!important}}.box label,.card label,.panel label{{margin-top:8px!important;margin-bottom:3px!important;font-size:12px!important}}.box input,.box select,.box textarea,.card input,.card select,.card textarea,.panel input,.panel select,.panel textarea{{padding:8px!important;margin-top:3px!important;margin-bottom:7px!important;border-radius:9px!important}}@media(max-width:850px){{.grid,.layout{{grid-template-columns:1fr!important}}}}@media print{{.darman-global-toolbar{{display:none}}}}</style>'''.encode('utf-8')
        if request.path == '/':
            response.content = response.content.replace(b'<a class="module" href="/imaging/">', '<a class="module" href="/laboratory/"><div class="mini">🧪</div><div><h3>آزمایشگاه</h3><p>پذیرش آزمایش، نمونه‌گیری و ثبت نتایج</p></div></a><a class="module" href="/imaging/">'.encode('utf-8'), 1)
            toolbar += '<a href="/laboratory/" style="position:fixed;bottom:48px;right:24px;z-index:9998;background:#138576;color:#fff;padding:12px 18px;border-radius:10px;text-decoration:none;font:13px Tahoma">🧪 کارتابل آزمایشگاه</a>'.encode('utf-8')
        marker = b'</body>'
        if marker in response.content:
            response.content = response.content.replace(marker, toolbar + marker, 1)
        return response
