from odoo import http
import base64
from odoo.http import request,Response
import json

class ProjectAPI(http.Controller):

    @http.route("/api/employees",auth='none',type='json',methods=["GET"], csrf=False)
    def get_employees_with_projects(self):

        auth_header = request.httprequest.headers.get('Authorization')
        if not auth_header:
            # If no Authorization header is found, return 401 Unauthorized
            return Response(json.dumps({'error': 'Unauthorized'}), content_type='application/json', status=401)

        # Decode the Base64 encoded username and password
        try:
            auth_type, auth_credentials = auth_header.split(' ', 1)

            if auth_type.lower() != 'basic':
                return Response(json.dumps({'error': 'Invalid Authentication Type'}), content_type='application/json',
                                status=401)

            # Decode the Base64 string to get the username and password
            username, password = base64.b64decode(auth_credentials.strip()).decode('utf-8').split(':', 1)
        except (ValueError, TypeError, base64.binascii.Error):
            return Response(json.dumps({'error': 'Invalid Authorization Header'}), content_type='application/json',
                            status=400)

        # Check the provided username and password against Odoo's users
        user_agent_env = request.httprequest.user_agent  # Get the user agent string

        user = request.env['res.users'].sudo().authenticate(request.env.cr.dbname, username, password,user_agent_env)

        # If the user is not authenticated, return an error
        if not user:
            return Response(json.dumps({'error': 'Invalid Credentials'}), content_type='application/json', status=401)
        employees = request.env['hr.employee'].sudo().search([])
        result = []
        for employee in employees:
            projects = employee.project_ids.filtered(lambda p: p.status == 'active')
            project_data = [{'name': proj.project_id.name} for proj in projects]
            result.append({'employee': employee.name, 'projects': project_data})

        # Directly return the result list; Odoo will handle JSON conversion
        return result