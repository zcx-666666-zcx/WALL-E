package com.example.demo.common;

public class Result<T> {
    private boolean success;
    private String message;
    private T data;
    private String error;

    public static <T> Result<T> success(T data) {
        Result<T> result = new Result<>();
        result.success = true;
        result.message = "操作成功";
        result.data = data;
        return result;
    }

    public static <T> Result<T> success(String message, T data) {
        Result<T> result = new Result<>();
        result.success = true;
        result.message = message;
        result.data = data;
        return result;
    }

    public static <T> Result<T> error(String errorMsg) {
        Result<T> result = new Result<>();
        result.success = false;
        result.error = errorMsg;
        return result;
    }

    // Getters and setters
    public boolean isSuccess() {
        return success;
    }

    public void setSuccess(boolean success) {
        this.success = success;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public T getData() {
        return data;
    }

    public void setData(T data) {
        this.data = data;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }
}