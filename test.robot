*** Settings ***
Library    lib/remote.py
Library    OperatingSystem
Library    Collections
Resource    lib/remote.resource
*** Variables ***
# ${S_HOST}    127.0.0.1
# ${S_PORT}    220
# ${S_USER}    kim
# ${S_PASS}    root
# ${S_DIR}     /home/kim/project/test_sip/

# ${C_HOST}    127.0.0.1
# ${C_PORT}    2200
# ${C_USER}    kim
# ${C_PASS}    root
# ${C_DIR}     /home/kim/project/test_sip/

${SCENARIO_LIST_DIR}    ./test_list.cfg
#${S_CMD}    sipp -sf /home/kim/project/test_sip/test_s.xml -i 10.0.2.15 -p 33333 -trace_msg -trace_err -m 1 recv_timeout 100000 -bg
#${C_CMD}    sipp -sf /home/kim/project/test_sip/test_c.xml -s 01050005001 -i 10.0.2.4 -p 33330 10.0.2.15:33333 -trace_msg -trace_err -r 1 -m 1 -l 1 -bg



*** Keywords ***

호스트 정보 세팅하기
    ${lsim}    ${rsim}    Get Host Info

    ${S_HOST}    Get From Dictionary    ${rsim}    HOST
    ${S_PORT}    Get From Dictionary    ${rsim}    PORT
    ${S_USER}    Get From Dictionary    ${rsim}    USER
    ${S_PASS}    Get From Dictionary    ${rsim}    PASS
    ${S_DIR}     Get From Dictionary    ${rsim}    DIR
    
    ${C_HOST}    Get From Dictionary    ${lsim}    HOST
    ${C_PORT}    Get From Dictionary    ${lsim}    PORT
    ${C_USER}    Get From Dictionary    ${lsim}    USER
    ${C_PASS}    Get From Dictionary    ${lsim}    PASS
    ${C_DIR}     Get From Dictionary    ${rsim}    DIR
    
    &{SERVER_INFO}    Create Dictionary    HOST=${S_HOST}     PORT=${S_PORT}    USER=${S_USER}    PW=${S_PASS}
    &{CLIENT_INFO}    Create Dictionary    HOST=${C_HOST}     PORT=${C_PORT}    USER=${C_USER}    PW=${C_PASS}

    Set Global Variable    ${SERVER_INFO}
    Set Global Variable    ${CLIENT_INFO}
    Set Global Variable    ${S_DIR}
    Set Global Variable    ${C_DIR}

시나리오 리스트 가져오기
    ${scenario_list}    get_scenario_list    ${SCENARIO_LIST_DIR}
    Set Global Variable    ${scenario_list}
    # RETURN    ${scenario_list}

시나리오 업로드
    #시나리오 업로드 후 파일위치 반환
    [Arguments]    ${SCENARIO_DIR}
    ${s_scenario_file}    get_scenario_file    ${SCENARIO_DIR}    server
    ${c_scenario_file}    get_scenario_file    ${SCENARIO_DIR}    client
    upload_scenario    ${SERVER_INFO}    ./${s_scenario_file[0]}    ${S_DIR}${s_scenario_file[1]}
    upload_scenario    ${CLIENT_INFO}    ./${c_scenario_file[0]}    ${C_DIR}${c_scenario_file[1]}
    ${SERVER_XML_FILE}    Set Variable    ${S_DIR}${s_scenario_file[1]}
    ${CLIENT_XML_FILE}    Set Variable    ${C_DIR}${c_scenario_file[1]}
    Set Global Variable    ${SERVER_XML_FILE}
    Set Global Variable    ${CLIENT_XML_FILE}

로그 디렉토리 만들기
    [Arguments]    ${SCENARIO_DIR}
    ${time_now}    Get Datetime
    ${local_log_dir}    make_log_dir    ${SCENARIO_DIR}/log    ${time_now}
    Set Global Variable    ${local_log_dir}

시나리오 실행
    #커맨드 설정
    ${S_CMD}    Set Variable    sipp -sf ${SERVER_XML_FILE} -i 10.0.2.15 -p 33333 -trace_msg -trace_err -m 1 -watchdog_minor_threshold 100000000 -bg
    ${C_CMD}    Set Variable    sipp -sf ${CLIENT_XML_FILE} -s 01050005001 -i 10.0.2.4 -p 33330 10.0.2.15:33333 -trace_msg -trace_err -r 1 -m 1 -l 1 -watchdog_minor_threshold 100000000 -bg

    #시나리오 실행
    ${server_output}    exec_scenario    ${SERVER_INFO}    ${S_CMD}
    ${client_output}    exec_scenario    ${CLIENT_INFO}    ${C_CMD}

    #시나리오 끝날때 까지 대기
    wait_end    ${SERVER_INFO}    ${server_output[0]}
    wait_end    ${CLIENT_INFO}    ${client_output[0]}

로그파일 옮기기    #VM에 작성된 로그를 Local로
    mv_log_file    ${SERVER_INFO}    ${S_DIR}    ${local_log_dir}/s
    mv_log_file    ${CLIENT_INFO}    ${C_DIR}    ${local_log_dir}/c

리시브 로그 만들기    #리시브만 기록된 로그 파일 기록
    write_receive_log    ${local_log_dir}/s
    write_receive_log    ${local_log_dir}/c

서머리 만들기
    check_scenario_rule    ${local_log_dir}/    server
    check_scenario_rule    ${local_log_dir}/    client

최근 기록 만들기
    make_recent_log    ${local_log_dir}/

업로드했던 모든파일과 로그삭제
    delete_all_file    ${SERVER_INFO}    rm ${S_DIR}*.log ${S_DIR}*.xml
    delete_all_file    ${CLIENT_INFO}    rm ${C_DIR}*.log ${C_DIR}*.xml






*** Test Cases ***
Work
    호스트 정보 세팅하기
    시나리오 리스트 가져오기
    FOR    ${scenario}    IN    @{scenario_list}
        로그 디렉토리 만들기    ${scenario}
        시나리오 업로드    ${scenario}
        시나리오 실행
        로그파일 옮기기
        리시브 로그 만들기
        서머리 만들기
        최근 기록 만들기
        업로드했던 모든파일과 로그삭제
    END

    
