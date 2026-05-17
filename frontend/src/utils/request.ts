const BASE_URL = "http://localhost:8000";

interface RequestOptions {
  method?: "GET" | "POST" | "PUT" | "DELETE";
  data?: Record<string, any>;
  header?: Record<string, string>;
}

export function request<T = any>(url: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", data, header = {} } = options;

  const token = uni.getStorageSync("token");
  if (token) {
    header["Authorization"] = `Bearer ${token}`;
  }

  return new Promise((resolve, reject) => {
    uni.request({
      url: BASE_URL + url,
      method,
      data,
      header,
      success: (res: any) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else {
          reject(res.data);
        }
      },
      fail: (err: any) => {
        reject(err);
      },
    });
  });
}