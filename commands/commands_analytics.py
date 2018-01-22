from apiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_LOCATION = 'g_an_key.json'
VIEW_ID = '161387953'


def initialize_analyticsreporting():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        KEY_FILE_LOCATION, SCOPES)
    analytics = discovery.build('analyticsreporting', 'v4', credentials=credentials)
    return analytics


def get_report(analytics):
    return analytics.reports().batchGet(
        body={
            'reportRequests': [
                {
                    'viewId': VIEW_ID,
                    'dateRanges': [{'startDate': 'yesterday', 'endDate': 'today'}],
                    'metrics': [{'expression': 'ga:users'}]
                }]
        }
    ).execute()


def get_values(response):
    r_rp = []
    for report in response.get('reports', []):
        column_header = report.get('columnHeader', {})
        metric_headers = column_header.get('metricHeader', {}).get('metricHeaderEntries', [])
        for row in report.get('data', {}).get('rows', []):
            date_range_values = row.get('metrics', [])
            for i, values in enumerate(date_range_values):
                for metric_header, value in zip(metric_headers, values.get('values')):
                    r_rp.append([metric_header.get('name'), value])
    return r_rp


def get_reports():
    analytics = initialize_analyticsreporting()
    report = get_report(analytics)
    return get_values(report)
