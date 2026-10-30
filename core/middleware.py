class AdmissionConfirmationMiddleware:
    """Ask for confirmation before any final-admission form is submitted."""
    marker = b'</body>'
    script = """<style>.actions a[href='/dentistry/setup/'],.top a[href='/definitions/import/']{display:none!important}</style><script>document.addEventListener('submit',function(e){var f=e.target,b=f.querySelector('button[type=submit],button:not([type])');if(!b||!/(ثبت پذیرش|صدور ارجاع)/.test(b.textContent)||f.dataset.confirmed)return;if(!confirm('آیا از ثبت نهایی پذیرش و صدور کد ارجاع مطمئن هستید؟')){e.preventDefault()}else{f.dataset.confirmed='1'}});(function(){var code=new URLSearchParams(location.search).get('ref');if(!code)return;var a=document.createElement('a');a.href='/reception/edit/'+encodeURIComponent(code)+'/';a.textContent='ویرایش پذیرش تا قبل از تسویه';a.style='position:fixed;left:20px;bottom:20px;background:#147d70;color:#fff;padding:11px 14px;border-radius:9px;text-decoration:none;font-family:Tahoma;z-index:99';document.body.appendChild(a)})()</script>""".encode()
    def __init__(self, get_response): self.get_response = get_response
    def __call__(self, request):
        response = self.get_response(request)
        if response.get('Content-Type', '').startswith('text/html') and getattr(response, 'content', None) and self.marker in response.content:
            response.content = response.content.replace(self.marker, self.script + self.marker)
            response['Content-Length'] = str(len(response.content))
        return response
