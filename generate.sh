#! /bin/sh

mkdir test

python3 adc_add_sbb_sub.py test
python3 adc16_add16_sbb16_sub16.py test
python3 cbw_cwd.py test
python3 cmp.py test
python3 cmp16.py test
# python3 bcd.py test
python3 inc_dec.py test
python3 inc_dec16.py test
python3 jmp_call_ret.py test
./jmp_call_ret_far.sh test
./jmp_call_ret_far2.sh test
python3 misc.py test
python3 misc2.py test
python3 misc2b.py test
python3 misc3.py test
python3 mov.py test
python3 neg.py test
python3 or_and_xor_test.py test
python3 or_and_xor_test_16.py test
python3 push_pop.py test
python3 rcl_rcr_rol_ror_sal_sar.py test
python3 strings.py test
