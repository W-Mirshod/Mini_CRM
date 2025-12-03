from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from .routers import operators, sources, contacts, view
import re

app = FastAPI(title="Mini-CRM Lead Distribution")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

class OpenGraphMiddleware(BaseHTTPMiddleware):
    """Add Open Graph meta tags to all HTML responses"""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Only process HTML responses
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('text/html'):
            return response
        
        # Read response body from iterator
        body = b""
        async for chunk in response.body_iterator:
            body += chunk
        
        if not body:
            return response
        
        try:
            body_str = body.decode('utf-8', errors='ignore')
        except:
            return response
        
        # Check if meta tags already exist
        if 'og:title' in body_str.lower():
            # Return original response but we need to recreate it since we consumed the iterator
            return HTMLResponse(
                content=body_str,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
        
        # Generate meta tags
        base_url = f"{request.url.scheme}://{request.url.netloc}"
        meta_tags = f'''
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="{request.url}">
    <meta property="og:title" content="Mini-CRM Lead Distribution System">
    <meta property="og:description" content="Professional lead distribution system for CRM operations. Distribute leads efficiently across multiple operators with customizable weights and real-time statistics.">
    <meta property="og:image" content="{base_url}/static/preview.svg">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:site_name" content="Mini-CRM">

    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:url" content="{request.url}">
    <meta name="twitter:title" content="Mini-CRM Lead Distribution System">
    <meta name="twitter:description" content="Professional lead distribution system for CRM operations. Distribute leads efficiently across multiple operators with customizable weights and real-time statistics.">
    <meta name="twitter:image" content="{base_url}/static/preview.svg">
'''
        
        # Insert before </head> or at the beginning if no </head>
        if re.search(r'</head>', body_str, re.IGNORECASE):
            body_str = re.sub(
                r'</head>',
                meta_tags + '    </head>',
                body_str,
                flags=re.IGNORECASE
            )
        elif re.search(r'<body', body_str, re.IGNORECASE):
            # If no head tag, add before body
            body_str = re.sub(
                r'<body',
                '<head>' + meta_tags + '</head>\n<body',
                body_str,
                flags=re.IGNORECASE
            )
        else:
            # If no head or body, prepend
            body_str = '<!DOCTYPE html><html><head>' + meta_tags + '</head><body>' + body_str + '</body></html>'
        
        # Create new response with updated headers
        new_headers = dict(response.headers)
        # Remove Content-Length as it will be recalculated
        new_headers.pop('content-length', None)
        
        return HTMLResponse(
            content=body_str,
            status_code=response.status_code,
            headers=new_headers
        )

# Add middleware
app.add_middleware(OpenGraphMiddleware)

app.include_router(operators.router)
app.include_router(sources.router)
app.include_router(contacts.router)
app.include_router(view.router)

@app.get("/")
async def root():
    return {"message": "Mini-CRM is running"}

@app.get("/docs")
async def swagger_ui(request: Request):
    """Custom Swagger UI with Open Graph meta tags"""
    return templates.TemplateResponse("swagger.html", {"request": request})
