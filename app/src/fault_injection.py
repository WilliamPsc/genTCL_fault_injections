####
## @Author : William PENSEC
## @Version : 0.0
## @Date : 20 janvier 2023
## @Description : 
####

### Import packages ###


### Class ###
class FaultInjection:
    def __init__(self, config_data):
        self.__simulator = config_data["name_simulator"]

    def inject_fault(self, threat, bit_flipped_0 = 0, bit_flipped_1 = 0, size_reg_0 = 1, size_reg_1 = 1):
        match threat:
            case "set0":
                return self.__set0()
            case "set1":
                return self.__set1()
            case "bitflip":
                return self.__bitflip(bit_flipped_0)
            case "multi_bitflip_spatial":
                return self.__multi_bitflip_spatial(bit_flipped_0, bit_flipped_1, size_reg_0, size_reg_1)
            case "multi_bitflip_temporel":
                pass
            case _:
                return ""

    def __set0(self):
        """Return the code to inject a fault in case of a bit reset fault injection scenario"""
        return """
if {$threat == "set0"} {
    if {$faulted_register == "/tb/top_i/core_region_i/RISCV_CORE/id_stage_i/registers_i_tag/rf_reg"} {
        for {set j 0} {$j < [llength $faulted_register]} {incr j} {
            force -freeze /tb/top_i/core_region_i/RISCV_CORE/id_stage_i/registers_i_tag/rf_reg\[{$j}\] "1'h0" 0 -cancel "$half_periode ns"
        }
    } else {
        force -freeze $faulted_register 0 0 -cancel "$half_periode ns"
    }  
}
"""

    def __set1(self):
        """Return the code to inject a fault in case of a bit set fault injection scenario"""
        return """
if {$threat == "set1"} {
    if {$width_threat == 1} {
        force -freeze $faulted_register 1'h1 0 -cancel "$half_periode ns"
    } else {
        force -freeze $faulted_register [concat [expr $width_threat]'h[string repeat F $width_threat]] 0 -cancel "$half_periode ns"
    }
}
"""

    def __bitflip(self, bit_flipped_0):
        return """
if {{$threat == "bitflip"}} {{
    if {{$width_threat == 1}} {{
        set value_curr_reg [examine -bin $faulted_register]
        set value [lindex [split $value_curr_reg b] 1]
        set bf [expr {{$value^1}}]
        set bit_flipped 0
        force -freeze $faulted_register $bf 0 -cancel "$half_periode ns"
    }} else {{
        set bit_attacked {wreg}
        set bit_flipped $bit_attacked
        set value_curr_reg [examine -hex $faulted_register\[{{$bit_attacked}}\]]
        set value [lindex [split $value_curr_reg h] 1]
        set bitflip_faulted_register [expr $value^1]
        force -freeze $faulted_register\[{{$bit_attacked}}\] [concat $width_threat'h$bitflip_faulted_register] 0 -cancel "$half_periode ns"
    }}
}}
""".format(wreg = bit_flipped_0)
    
    def __multi_bitflip_spatial(self, bit_flipped_0, bit_flipped_1, size_reg_0, size_reg_1):
        """Generate code for a spatial multi-bit-flip fault threat model"""
        if(size_reg_0 == 1 and size_reg_1 == 1):
            return """
# Both registers size are equal to 1
## Bit flip registre 0
set value_curr_reg [examine -bin $faulted_register_0]
set value [lindex [split $value_curr_reg b] 1]
set bf [expr {$value^1}]
set bit_flipped_0 0
force -freeze $faulted_register_0 $bf 0 -cancel "$half_periode ns"

## Bit flip registre 1
set value_curr_reg [examine -bin $faulted_register_1]
set value [lindex [split $value_curr_reg b] 1]
set bf [expr {$value^1}]
set bit_flipped_1 0
force -freeze $faulted_register_1 $bf 0 -cancel "$half_periode ns"
"""
        elif(size_reg_0 > 1 and size_reg_1 == 1):
            return """
# The first register size is different of 1, we flip the bit indicated in arg 1, the other register size is equal to 1
## Bit flip registre 0
set bit_attacked {wreg_0}
set bit_flipped_0 $bit_attacked
set value_curr_reg [examine -bin $faulted_register_0\[{{$bit_attacked}}\]]
set value [lindex [split $value_curr_reg b] 1]
set bitflip_faulted_register_0 [expr $value^1]
force -freeze $faulted_register_0\[{{$bit_attacked}}\] [concat $width_register_0'b$bitflip_faulted_register_0] 0 -cancel "$half_periode ns"

## Bit flip registre 1
set value_curr_reg [examine -bin $faulted_register_1]
set value [lindex [split $value_curr_reg b] 1]
set bf [expr {{$value^1}}]
set bit_flipped_1 0
force -freeze $faulted_register_1 $bf 0 -cancel "$half_periode ns"
""".format(wreg_0 = bit_flipped_0)
        elif(size_reg_0 == 1 and size_reg_1 > 1):
            return """
# The first register size is equal to 1, the second is different of 1 so we flip the bit indicated in arg 2
## Bit flip registre 0
set value_curr_reg [examine -bin $faulted_register_0]
set value [lindex [split $value_curr_reg b] 1]
set bf [expr {{$value^1}}]
set bit_flipped_0 0
force -freeze $faulted_register_0 $bf 0 -cancel "$half_periode ns"

## Bit flip registre 1
set bit_attacked {wreg_1}
set bit_flipped_1 $bit_attacked
set value_curr_reg [examine -bin $faulted_register_1\[{{$bit_attacked}}\]]
set value [lindex [split $value_curr_reg b] 1]
set bitflip_faulted_register_1 [expr $value^1]
force -freeze $faulted_register_1\[{{$bit_attacked}}\] [concat $width_register_1'b$bitflip_faulted_register_1] 0 -cancel "$half_periode ns"
""".format(wreg_1 = bit_flipped_1)
        elif(size_reg_0 > 1 and size_reg_1 > 1):
            return """
# Both registers sizes are different of 1, we flip the bit indicated in arg 1 and 2
## Bit flip registre 0
set bit_attacked {wreg_0}
set bit_flipped_0 $bit_attacked
set value_curr_reg [examine -bin $faulted_register_0\[{{$bit_attacked}}\]]
set value [lindex [split $value_curr_reg b] 1]
set bitflip_faulted_register_0 [expr $value^1]
force -freeze $faulted_register_0\[{{$bit_attacked}}\] [concat $width_register_0'b$bitflip_faulted_register_0] 0 -cancel "$half_periode ns"

## Bit flip registre 1
set bit_attacked {wreg_1}
set bit_flipped_1 $bit_attacked
set value_curr_reg [examine -bin $faulted_register_1\[{{$bit_attacked}}\]]
set value [lindex [split $value_curr_reg b] 1]
set bitflip_faulted_register_1 [expr $value^1]
force -freeze $faulted_register_1\[{{$bit_attacked}}\] [concat $width_register_1'b$bitflip_faulted_register_1] 0 -cancel "$half_periode ns"
""".format(wreg_0 = bit_flipped_0, wreg_1 = bit_flipped_1)
        else:
            print("Erreur de paramètres ! ", size_reg_0, size_reg_1)
            exit(2)

    def __multi_bitflip_temporel(self):
        """Generate code for a multi-bit-flip temporal fault threat model"""
        pass