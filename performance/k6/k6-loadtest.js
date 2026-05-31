import http from 'k6/http';
import { check, fail, sleep } from 'k6';

export const options = {
  vus: Number(__ENV.VUS || 50),
  duration: __ENV.DURATION || '1m',
  thresholds: {
    http_req_failed: ['rate<0.05'],
    http_req_duration: ['p(95)<1000'],
  },
  tags: {
    project: 'uclv_residencias',
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const LOGIN_PATH = __ENV.LOGIN_PATH || '/api/v1/auth/login/';
const TARGET_PATH = __ENV.TARGET_PATH || '/api/v1/estudiantes/';
const USERNAME = __ENV.USERNAME || 'admin_bd';
const PASSWORD = __ENV.PASSWORD || 'Password123!';

export function setup() {
  const loginResponse = http.post(
    `${BASE_URL}${LOGIN_PATH}`,
    JSON.stringify({
      username: USERNAME,
      password: PASSWORD,
    }),
    {
      headers: {
        'Content-Type': 'application/json',
      },
    }
  );

  console.log(`Login status: ${loginResponse.status}`);
  console.log(`Login body: ${loginResponse.body}`);

  check(loginResponse, {
    'login responde 200': (response) => response.status === 200,
    'login devuelve access': (response) => Boolean(response.json('access')),
  });

  if (loginResponse.status !== 200) {
    fail(`Login failed with status ${loginResponse.status}: ${loginResponse.body}`);
  }

  const accessToken = loginResponse.json('access');
  if (!accessToken) {
    fail('No access token in login response');
  }

  return {
    access: accessToken,
  };
}

export default function (data) {
  const response = http.get(`${BASE_URL}${TARGET_PATH}`, {
    headers: {
      Authorization: `Bearer ${data.access}`,
    },
  });

  check(response, {
    'respuesta 200': (res) => res.status === 200,
  });

  sleep(1);
}