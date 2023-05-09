class Err:
    def __init__(self):
        #에러 리스트 정의
        self.err_list = {
            1062: "같은 이름이 존재합니다",
            1048: "필수 입력란은 확인해 주세요",
            1366: "필수 입력란을 확인해 주세요"
        }

    #에러 코드에 맞는 문구 출력 
    def print(self, err_code):
        try:
            result = self.err_list[err_code]
        except:
            #에러 코드가 에러리스트에 정의 되어 있지 않을 경우 아래 내용 출력
            result = "알 수 없는 에러가 발생했습니다"

        return result