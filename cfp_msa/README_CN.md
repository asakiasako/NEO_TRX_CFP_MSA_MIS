CFP MSA MIS Interface Userguide
===

CMIS python 库依据 CFP MSA MIS Version 2.6 r06a，将符合 CMIS 协议的模块抽象出来，以达到统一接口的目的。

CMIS 接口的设计原则是：

1. 与 CFP MSA MIS 协议的一致性。所有专有名词和描述方式与 CMIS 协议保持一致。
2. 直观，简洁，易用。大部分基础操作可以采用运算符实现，不需要调用函数，使用更为便捷。

对于 CFP MSA MIS 协议规定的某些名词或缩写，本文档将直接引用，不做额外的解释。所有专有名词与 CFP MSA MIS 协议保持严格一致。

CFP MSA MIS 接口主要包含以下几个方面的内容：

I. 基础管理接口

1. CFP MSA MIS Signal Pins
2. MDIO register and bits operations

II. 应用接口

1. Module State Machine
2. Other informations, e.g. Module PN/SN, etc.
3. Extended applications, e.g. get Pre-Fec BER

下面详细介绍这些接口。

## 接口设计

### 基础管理接口

1. Signal Pins

    CFP MSA MIS Signal Pins 是由对应模块的封装协议所规定的信号名称，对应物理 pin 脚的电平高低。以 CFP 或 CFP2 为例，包括 MOD_RSTn, MOD_LOPWR, TX_DIS, PRG_CNTL1, PRG_CNTL2, PRG_CNTL3, RX_LOS, MOD_ABS, GLB_ALRMn, PRG_ALRM1, PRG_ALRM2, PRG_ALRM3。我们只关注这些信号的逻辑值，而不关心其具体的物理实现。

    这些 Signal Pins 包括 Control Pins 和 Alarm Pins，只有 Control Pins 可以设置，Alarm Pins 只能读取它的状态而无法进行设置。

    CfpMsaMis 对象接收 hw_type 作为参数，在对象初始化时根据这个参数来确定其具有哪些 Signal Pins。

    使用 `[]` 操作符对这些信号进行读写操作，赋值或返回一个 bool 类型。`[]` 操作符内填写 Pin 的名称，与协议规定的信号名称严格一致。

    以 CFP2 模块为例：

    - 读取信号

        ``` python
        state = cmis['TX_DIS']  # returns a bool
        ```

    - 设置信号

        对于无法被设置的信号，抛出一个 PermissionError

        ``` python
        cmis['TX_DIS'] = True   # set TX_DIS to high voltage level
        cmis['RX_LOS'] = True      # raise a PermissionError
        ```

2. MDIO register and bits operations

    CFP MSA MIS 兼容模块使用 MDIO 来对模块内的寄存器进行读写访问。通过 `[]` 操作符，可以对寄存器进行随机读写（Random Read/Write）和随机序列读写（Sequential Read from Random Start Address/Sequential Write）。

    对于读取单个寄存器所得到的寄存器值（事实上是一个 RegisterValue 对象），还可以进一步对其进行位和位区间的读写操作。

    注意，对于 Sequential Read，目前仅仅是通过多次 Random Read 来实现的。

    - Random Byte Read Operation

        `[]` 操作符接收寄存器的地址（int）作为参数，返回一个 RegisterValue 对象。这个对象是一个 int-like 对象，支持 int 对象的所有操作，它的值与寄存器所表示的无符号整数的值相等。

        ``` python
        reg_value = cfp[0x8000]  # returns a RegisterValue object
        ```

        如果你需要该寄存器所代表的有符号整数的值，可以使用 `RegisterValue.to_signed()` 方法，该方法返回一个被转换为有符号整数的 int。

        ``` python
        val = cfp[0x8000].to_signed()
        ```

        如果指定的地址超过了 CFP_MSA_MIS 协议规定的有效范围（0x0000~0xFFFF），将抛出一个 `IndexError`。

        对 RegisterValue 还可以进行进一步的位操作，将在后文中描述。

    - Byte Write Operation

        `[]` 操作符接受寄存器的地址（int）作为参数，赋值一个 int 对象。该 int 对象将作为寄存器所表示的无符号整数写入寄存器。

        ``` python
        cmis[0x7F] = 0x10
        ```

        如果指定的地址超过了 CFP MSA MIS 协议规定的有效范围（0x0000~0xFFFF），将抛出一个 `IndexError`。如果赋值超过了寄存器所能表示的无符号整数的范围（0x0000~0xFFFF），将抛出一个 `ValueError`。

    - Sequential Read from Random Start Address

        `[]` 操作符接收寄存器地址的起止位作为参数，返回一个 `RegisterSequence` 对象。这个对象是一个由 int 所组成的 Sequential 对象，它的值与寄存器序列的值一一对应。

        该操作主要用于将一段寄存器序列通过 sequential read 的方式读取出来。

        ``` python
        val = cfp[0x8000:0x8001]
        # Sequential Reads register: 0x8000, 0x8001
        # Returns an RegisterSequence object
        ```

        需要注意的是，在 Sequential Read 操作中，寄存器地址的起止位都被包含在所需要读取的地址序列中。例如：`cmis[0x0000:0x0003]` 将读取 4 个地址，最后一位 `0x0003` 也被包括其中。这点与 python 中大多数序列的一般表示不同。这样设计的原因一是为了与 `CFP MSA MIS` 对于寄存器序列的表达形式相一致；二是对于寄存器表来说，这种表达方式更为直观和优雅，因为寄存器的地址序列完全由整数构成。你肯定不希望你的代码里出现 `cmis[0xFFFE:0x10000]` 这种丑陋的表达，因为 `0x10000` 这个地址在寄存器中并不存在。

        如果你需要获得寄存器序列所对应的整数值，你可以使用 `to_signed` 和 `to_unsigned` 方法，将其转换成 `int` 类型（分别视为 `signed int` 和 `unsigned int`）。RegisterSequence 对象还提供了 `to_asicc_str` 方法方便将一段寄存器序列转化为 ASCII 字符串。这在读取某些 ASCII 序列（例如模块的 Part Number）时十分有用。

        ``` python
        cfp[0x7000:0x7001].to_signed()
        cfp[0x7000:0x7001].to_unsigned()
        cfp[0x7000:7003].to_ascii_str()
        ```

        如果序列中的任何一个地址超过了 MDIO 地址的有效范围（0x0000~0xFFFF），将抛出一个 `IndexError`。

    - Sequential Byte Write Operation

        该操作用于将一段寄存器序列作为整体，接受赋值。赋值的类型可以是整数构成的序列，也可以是 `int` 类型。对于序列，例如整数列表，每个整数将一一对应写入寄存器内，序列的长度与寄存器区间的长度严格相等；对于 `int` 类型，应以 `unsigned` 的形式写入，且数据的值不能超过寄存器序列所能表示的最大无符号整数的值。对于不符合要求的数据，将抛出 `ValueError`。

        需要注意的是，由于 bytes 也是整数序列，因此写入每个寄存器的值将只有 1 个 byte，而不是两个 byte。每个寄存器的值为一个 word （即 2 bytes）。你需要将 bytes 转换成以 word 为元素的整数序列，才能正确写入。

        ``` python
        cfp[0x7000:0x7001] = 0x10010100
        # OR
        cfp[0x7000:0x7001] = [0x1001, 0x0100]
        ```

        如果序列的任何一个地址超过了 MDIO 地址的有效范围（0x0000~0xFFFF），将抛出一个 `IndexError`。如果所赋值的数据不符合要求，将抛出一个 `ValueError`。

    - Bits Read Operation

        对于读取寄存器所获得的 `RegisterValue` 对象，还可以进一步进行位的读写操作。既可以读取某个位的值，也可以读取几个连续位组成的位区间。

        对 RegisterValue 读取位或位序列，将返回一个整数，该整数的值为这段位或位序列所表示的无符号整数。

        ``` python
        v_bit3 = cfp[0x0003][3]      # value of 0x30.3
        v_bit7_3 = cfp[0x0003][7:4]  # value of 0x30.7-3
        ```

        由于寄存器位中，bit 15 为 MSB，因此一个寄存器序列的起始位总是大于终止位，如果起始位小于终止位，将抛出 `IndexError`：

        ``` python
        v_bits = cfp[0x0003][4:7]
        >>> ValueError(...)
        ```

        如果任意位号超过了寄存器的位号范围（0~15），将抛出 `IndexError`。

        需要注意的是，在该操作中，位号的起止位都被包含在所需要读取的位序列中。例如：`cfp[0x0003][7:4]` 将读取 4 个位，最后一位 `bit4` 也被包括其中。这点与序列的一般操作不同。这样设计的原因一是为了与 `CMIS` 对于寄存器位的表达相一致；二是对于寄存器表来说，这种表达方式更为合适、直观、优雅。你肯定不希望你的代码里出现 `cmis[0x0003][3:-1]` 这种丑陋的表达，竟然出现了负数的位号，这显然很别扭。

        事实上，该操作只是对已经获取的 `RegisterValue` 值所做的数学处理。真正的读取操作早在 `RegisterValue` 生成时就已经完成了。

    - Bits Write Operation

        类似的，你可以将合适的整数赋值给一个寄存器位或者位序列。

        ``` python
        cmis[0x0003][7:4] = 0b1011
        ```

        由于寄存器位中，bit 7 为 MSB，因此一个寄存器序列的起始位总是大于终止位，如果起始位小于终止位，将抛出 `IndexError`。如果任意位号超过了寄存器的位号范围（0~7），将抛出 `IndexError`。如果赋值的整数超过了寄存器位或位序列所能容纳的无符号整数范围，将抛出 `ValueError`。

        同样的，寄存器位号的起止位都包含在所需读取的寄存器位序列中。

        事实上，该操作首先对应获取的 `RegisterValue` 做数学处理，替换掉所写入的位或位序列，然后将新的值写回寄存器中。

### 应用接口

1. Module State Machine

    - `cfp.get_module_state()`

        返回模块状态字符串，与 CFP MSA MIS 协议所规定的标准命名相一致。

        例如：`'Module Ready'`

        更多细节参考 CFP MSA MIS 协议。

2. Information

3. Other applications
