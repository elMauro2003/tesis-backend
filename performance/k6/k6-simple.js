import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 1,
  duration: '10s',
};

export default function () {
  // Login en cada iteración
  const loginResponse = http.post('http://localhost:8000/api/v1/auth/login/', 
    JSON.stringify({
      username: 'admin_bd',
      password: 'Password123!'
    }),
    {
      headers: {
        'Content-Type': 'application/json',
      },
    }
  );

  console.log(`Login response status: ${loginResponse.status}`);
  
  check(loginResponse, {
    'login status 200': (r) => r.status === 200,
  });

  if (loginResponse.status === 200) {
    const token = loginResponse.json('access');
    
    // Hacer request autenticado
    const apiResponse = http.get('http://localhost:8000/api/v1/facultades/', {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    check(apiResponse, {
      'api status 200': (r) => r.status === 200,
    });
  }

  sleep(1);
}
